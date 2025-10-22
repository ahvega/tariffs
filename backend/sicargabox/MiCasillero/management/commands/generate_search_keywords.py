from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.postgres.search import SearchVector
from MiCasillero.models import PartidaArancelaria
import json
import os
from openai import OpenAI
from django.conf import settings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Command(BaseCommand):
    help = 'Genera keywords de búsqueda y vectores de búsqueda para las partidas arancelarias'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula la generación sin hacer cambios reales',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Número de partidas a procesar por lote',
        )
        parser.add_argument(
            '--start-from',
            type=int,
            default=0,
            help='ID de partida desde donde comenzar',
        )
        parser.add_argument(
            '--api-provider',
            type=str,
            default='deepseek',
            choices=['openai', 'deepseek', 'anthropic'],
            help='Proveedor de API a utilizar',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Número máximo total de partidas a procesar (opcional)',
        )

    def get_context_for_partida(self, partida):
        """Obtiene el contexto relevante de una partida."""
        # Obtener la descripción padre (después del primer |)
        parent_desc = partida.descripcion.split('|')[1].strip() if '|' in partida.descripcion else None
        
        # Obtener la descripción específica (antes del primer |)
        specific_desc = partida.descripcion.split('|')[0].strip() if '|' in partida.descripcion else partida.descripcion
        
        # Determinar si es una partida "Los demás"
        is_others = specific_desc.lower().startswith('los demás')
        
        # Determinar si la descripción específica está en la descripción padre
        is_specific_in_parent = specific_desc in parent_desc if parent_desc else False
        
        # Obtener partidas relacionadas basadas en la descripción padre
        if parent_desc:
            # Obtener todas las partidas que comparten la misma descripción padre
            # Limitar a 20 siblings para evitar exceder el límite de contexto (131K tokens)
            siblings = PartidaArancelaria.objects.filter(
                descripcion__contains=parent_desc
            ).exclude(id=partida.id).order_by('item_no')[:20]
            
            # Obtener las descripciones específicas de las partidas hermanas
            sibling_specific_descs = [
                s.descripcion.split('|')[0].strip() if '|' in s.descripcion else s.descripcion
                for s in siblings
            ]
            
            # Para partidas "Los demás", necesitamos excluir términos específicos
            if is_others:
                # Si hay una excepción específica (después de "excepto")
                if "excepto" in specific_desc.lower():
                    # Obtener el término de excepción
                    exception_term = specific_desc.lower().split("excepto")[1].strip()
                    # Obtener términos específicos de partidas hermanas que no son "Los demás"
                    excluded_terms = [
                        desc for desc in sibling_specific_descs 
                        if not desc.lower().startswith('los demás')
                    ]
                    # Agregar el término de excepción a los términos excluidos
                    excluded_terms.append(exception_term)
                else:
                    # Si no hay excepción específica, excluir todos los términos específicos
                    excluded_terms = [
                        desc for desc in sibling_specific_descs 
                        if not desc.lower().startswith('los demás')
                    ]
            else:
                excluded_terms = []
        else:
            siblings = []
            sibling_specific_descs = []
            excluded_terms = []
        
        context = {
            'current': {
                'codigo': partida.item_no,
                'description': partida.descripcion,
                'specific_desc': specific_desc,
                'parent_desc': parent_desc,
                'is_others': is_others,
                'is_specific_in_parent': is_specific_in_parent,
                'has_exception': "excepto" in specific_desc.lower() if is_others else False,
                'exception_term': specific_desc.lower().split("excepto")[1].strip() if is_others and "excepto" in specific_desc.lower() else None
            },
            'siblings': [{
                'codigo': p.item_no,
                'description': p.descripcion,
                'specific_desc': p.descripcion.split('|')[0].strip() if '|' in p.descripcion else p.descripcion
            } for p in siblings],
            'sibling_specific_descs': sibling_specific_descs,
            'excluded_terms': excluded_terms
        }
        return context

    def get_ai_client(self, api_provider):
        """Configura y retorna el cliente de AI según el proveedor seleccionado."""
        if api_provider == 'deepseek':
            import httpx
            client = OpenAI(
                base_url="https://api.deepseek.com/v1",
                api_key=os.environ.get('DEEPSEEK_API_KEY'),
                http_client=httpx.Client(),
            )
        elif api_provider == 'anthropic':
            from anthropic import Anthropic
            client = Anthropic(
                api_key=os.environ.get('ANTHROPIC_API_KEY'),
            )
        else:  # openai
            client = OpenAI(
                api_key=os.environ.get('OPENAI_API_KEY'),
            )
        return client

    def get_model_name(self, api_provider):
        """Retorna el nombre del modelo según el proveedor."""
        if api_provider == "deepseek":
            return "deepseek-chat"
        elif api_provider == "anthropic":
            return "claude-3-5-sonnet-20241022"
        else:
            return "gpt-3.5-turbo"

    def generate_keywords_with_ai(self, context, api_provider):
        """Usa AI para generar keywords basados en el contexto."""
        current = context['current']
        siblings = context['siblings']
        excluded_terms = context['excluded_terms']
        
        # Construir el prompt según el tipo de partida
        if current['is_others']:
            # Para "Los demás", excluir términos ya mencionados en hermanos
            if current['has_exception']:
                prompt = f"""
                Como experto en clasificación arancelaria, genera keywords de búsqueda para la siguiente partida:

                PARTIDA ACTUAL:
                Código: {current['codigo']}
                Descripción: {current['description']}

                IMPORTANTE: Esta es una partida "Los demás" con excepción específica:
                - Término principal: {current['parent_desc']}
                - Excepción: {current['exception_term']}
                - Términos a excluir: {json.dumps(excluded_terms, indent=2, ensure_ascii=False)}

                Genera una lista de keywords que:
                1. Incluya SOLO sinónimos y términos alternativos del término principal EXCEPTO:
                   - El término de excepción específico: {current['exception_term']}
                   - Los términos que ya tienen su propia partida: {json.dumps(excluded_terms, indent=2, ensure_ascii=False)}
                2. Se enfoque en variaciones y tipos no mencionados en las partidas anteriores
                3. Incluya términos técnicos y coloquiales relacionados
                4. Incluya variaciones regionales de los términos
                5. Incluya términos de búsqueda frecuentes del usuario final

                IMPORTANTE - BILINGUAL KEYWORDS (ENGLISH + SPANISH):
                Los usuarios copian descripciones de facturas estadounidenses (Amazon, eBay, etc.) en INGLÉS.

                REQUERIMIENTOS OBLIGATORIOS:
                - Keywords en INGLÉS Y ESPAÑOL (ambos idiomas son obligatorios)
                - Preservar términos técnicos exactos: "USB-C", "HDMI", "bluetooth 5.0", "LED", "GPS"
                - Incluir nombres de marcas comunes: "iPhone", "Samsung", "Nike", "Adidas"
                - Incluir números de modelo cuando relevante: "iPhone 15 Pro", "Galaxy S24"
                - Usuarios buscan en inglés, español, y mezcla de ambos idiomas

                EJEMPLOS DE KEYWORDS BILINGUAL:
                - Computadoras: ["laptop", "notebook", "computer", "pc", "computadora", "ordenador", "laptop computer"]
                - Teléfonos: ["smartphone", "phone", "mobile phone", "celular", "teléfono móvil", "iPhone", "android"]
                - Cables: ["USB-C cable", "cable USB-C", "HDMI", "HDMI cable", "charging cable", "cable de carga"]
                - Ropa: ["shoes", "sneakers", "zapatos", "tenis", "running shoes", "zapatillas"]

                IMPORTANTE:
                - NO incluyas términos relacionados con: {json.dumps(excluded_terms, indent=2, ensure_ascii=False)}
                - NO incluyas términos relacionados con: {current['exception_term']}
                - Responde SOLO con el array JSON, sin markdown, sin explicaciones.
                Ejemplo: ["laptop", "notebook", "computer", "computadora", "pc", "ordenador"]
                """
            else:
                prompt = f"""
                Como experto en clasificación arancelaria, genera keywords de búsqueda para la siguiente partida:

                PARTIDA ACTUAL:
                Código: {current['codigo']}
                Descripción: {current['description']}

                IMPORTANTE: Esta es una partida "Los demás" que debe EXCLUIR los siguientes términos que ya tienen su propia partida:
                {json.dumps(excluded_terms, indent=2, ensure_ascii=False)}

                Genera una lista de keywords que:
                1. Incluya SOLO sinónimos y términos alternativos de las palabras en la descripción padre que NO estén en la lista de términos excluidos
                2. Se enfoque en variaciones y tipos no mencionados en las partidas anteriores
                3. Incluya términos técnicos y coloquiales relacionados
                4. Incluya variaciones regionales de los términos
                5. Incluya términos de búsqueda frecuentes del usuario final

                IMPORTANTE - BILINGUAL KEYWORDS (ENGLISH + SPANISH):
                Los usuarios copian descripciones de facturas estadounidenses (Amazon, eBay, etc.) en INGLÉS.

                REQUERIMIENTOS OBLIGATORIOS:
                - Keywords en INGLÉS Y ESPAÑOL (ambos idiomas son obligatorios)
                - Preservar términos técnicos exactos: "USB-C", "HDMI", "bluetooth 5.0", "LED", "GPS"
                - Incluir nombres de marcas comunes cuando relevante
                - Usuarios frecuentemente buscan productos electrónicos/tecnológicos en inglés
                - Incluir variaciones comunes en ambos idiomas

                EJEMPLOS DE KEYWORDS BILINGUAL:
                - Electrónica: ["headphones", "earbuds", "auriculares", "audífonos", "wireless", "inalámbrico", "AirPods"]
                - Accesorios: ["case", "cover", "funda", "protector", "screen protector", "mica"]
                - Deportes: ["backpack", "mochila", "sports bag", "bolsa deportiva", "gym bag"]

                IMPORTANTE:
                - NO incluyas términos relacionados con: {json.dumps(excluded_terms, indent=2, ensure_ascii=False)}
                - Responde SOLO con el array JSON, sin markdown, sin explicaciones.
                Ejemplo: ["headphones", "earbuds", "auriculares", "audífonos", "wireless headphones"]
                """
        elif current['is_specific_in_parent']:
            # Para partidas con descripción específica en la padre
            prompt = f"""
            Como experto en clasificación arancelaria, genera keywords de búsqueda para la siguiente partida:

            PARTIDA ACTUAL:
            Código: {current['codigo']}
            Descripción específica: {current['specific_desc']}
            Descripción padre: {current['parent_desc']}

            IMPORTANTE: Esta partida se refiere específicamente a "{current['specific_desc']}".
            Genera una lista de keywords que:
            1. Se enfoque SOLO en sinónimos y variaciones de "{current['specific_desc']}"
            2. NO incluya términos relacionados con otras categorías en la descripción padre
            3. Incluya términos técnicos y coloquiales específicos
            4. Incluya variaciones regionales
            5. Incluya términos de búsqueda frecuentes del usuario final

            IMPORTANTE - BILINGUAL KEYWORDS (ENGLISH + SPANISH):
            Los usuarios copian descripciones de facturas estadounidenses (Amazon, eBay, etc.) en INGLÉS.

            REQUERIMIENTOS OBLIGATORIOS:
            - Keywords en INGLÉS Y ESPAÑOL (ambos idiomas son obligatorios)
            - Generar equivalentes en inglés de "{current['specific_desc']}"
            - Incluir nombres de marcas comunes si son relevantes para "{current['specific_desc']}"
            - Preservar términos técnicos: "USB-C", "HDMI", "bluetooth", "wifi", "LED", "GPS"
            - Productos tecnológicos frecuentemente buscados en inglés

            EJEMPLOS DE KEYWORDS BILINGUAL:
            - Si es "teclados": ["keyboard", "teclado", "mechanical keyboard", "teclado mecánico", "wireless keyboard", "gaming keyboard"]
            - Si es "cargadores": ["charger", "cargador", "power adapter", "adaptador", "USB charger", "wall charger"]
            - Si es "calzado deportivo": ["sports shoes", "sneakers", "running shoes", "zapatos deportivos", "tenis", "zapatillas"]

            IMPORTANTE: Responde SOLO con el array JSON, sin markdown, sin explicaciones.
            Ejemplo: ["keyboard", "teclado", "mechanical keyboard", "teclado mecánico", "wireless keyboard"]
            """
        else:
            # Para partidas normales
            prompt = f"""
            Como experto en clasificación arancelaria, genera keywords de búsqueda para la siguiente partida:

            PARTIDA ACTUAL:
            Código: {current['codigo']}
            Descripción: {current['description']}

            CONTEXTO JERÁRQUICO:
            Partidas Relacionadas:
            {json.dumps([p['description'] for p in siblings], indent=2, ensure_ascii=False)}

            Genera una lista de keywords que:
            1. Se enfoque SOLO en sinónimos y términos alternativos de "{current['specific_desc']}"
            2. NO incluya términos relacionados con otras categorías en la descripción padre
            3. Incluya términos técnicos y coloquiales específicos
            4. Incluya variaciones regionales
            5. Incluya términos de búsqueda frecuentes del usuario final

            IMPORTANTE - BILINGUAL KEYWORDS (ENGLISH + SPANISH):
            Los usuarios copian descripciones de facturas estadounidenses (Amazon, eBay, etc.) en INGLÉS.

            REQUERIMIENTOS OBLIGATORIOS:
            - Keywords en INGLÉS Y ESPAÑOL (ambos idiomas son obligatorios)
            - Generar equivalentes en inglés de los productos
            - Preservar términos técnicos exactos: "USB-C", "HDMI", "bluetooth", "wifi", "LED", "GPS", "NFC"
            - Incluir nombres de marcas comunes cuando relevante: "iPhone", "Samsung", "Nike", "Adidas", "Sony"
            - Usuarios frecuentemente buscan: "laptop", "smartphone", "mouse inalámbrico", "wireless headphones"
            - Incluir números de modelo cuando sea común: "iPhone 15", "Galaxy S24", "AirPods Pro"

            EJEMPLOS DE KEYWORDS BILINGUAL:
            - Computadoras: ["laptop", "notebook", "computer", "pc", "computadora", "ordenador", "MacBook", "Chromebook"]
            - Smartphones: ["smartphone", "phone", "mobile", "celular", "teléfono", "iPhone", "Galaxy", "android phone"]
            - Audio: ["headphones", "earbuds", "auriculares", "audífonos", "AirPods", "wireless earbuds", "bluetooth headphones"]
            - Accesorios tech: ["cable", "charger", "USB-C", "HDMI", "cargador", "cable de carga", "power bank", "adaptador"]
            - Ropa: ["shoes", "sneakers", "jacket", "zapatos", "tenis", "chaqueta", "hoodie", "sudadera"]

            IMPORTANTE: Responde SOLO con el array JSON, sin markdown, sin explicaciones.
            Ejemplo: ["laptop", "notebook", "computer", "computadora", "pc", "MacBook", "laptop computer"]
            """

        client = self.get_ai_client(api_provider)
        model = self.get_model_name(api_provider)
        system_message = "Eres un experto en clasificación arancelaria y comercio internacional. Genera máximo 30 keywords relevantes EN ESPAÑOL E INGLÉS (bilingual) para usuarios en Honduras que buscan productos copiando descripciones de facturas estadounidenses. Responde solo con arrays JSON puros, sin formato markdown."

        try:
            if api_provider == 'anthropic':
                # Anthropic API format
                response = client.messages.create(
                    model=model,
                    max_tokens=1200,
                    temperature=0.7,
                    system=system_message,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                response_text = response.content[0].text.strip()
            else:
                # OpenAI/DeepSeek API format
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1200
                )
                response_text = response.choices[0].message.content.strip()
            
            try:
                # Limpiar la respuesta de cualquier formato markdown
                clean_response = response_text.replace('```json', '').replace('```', '').strip()
                
                # Intentar parsear la respuesta como JSON
                keywords = json.loads(clean_response)
                if not isinstance(keywords, list):
                    return []
                    
                # Filtrar solo strings válidos y eliminar duplicados
                keywords = list(set([
                    k.lower().strip() 
                    for k in keywords 
                    if isinstance(k, str) and k.strip()
                ]))
                
                # Limitar la cantidad de keywords para no sobrecargar
                return keywords[:50]  # Limitamos a 50 keywords por partida
                
            except json.JSONDecodeError as e:
                self.stdout.write(self.style.WARNING(
                    f'Error al parsear respuesta AI:\n'
                    f'Respuesta original: {response_text}\n'
                    f'Respuesta limpia: {clean_response}\n'
                    f'Error: {str(e)}'
                ))
                return []
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al llamar a la API: {str(e)}'))
            return []

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        start_from = options['start_from']
        api_provider = options['api_provider']
        limit = options['limit']

        # Verificar API key
        if api_provider == 'deepseek':
            api_key = os.environ.get('DEEPSEEK_API_KEY')
        elif api_provider == 'anthropic':
            api_key = os.environ.get('ANTHROPIC_API_KEY')
        else:
            api_key = os.environ.get('OPENAI_API_KEY')

        if not api_key:
            self.stdout.write(self.style.ERROR(f'No se encontró la API key para {api_provider}'))
            return

        # Obtener todas las partidas
        partidas = PartidaArancelaria.objects.filter(
            id__gte=start_from
        ).order_by('id')

        # Aplicar límite si se especificó
        if limit:
            partidas = partidas[:limit]

        total_partidas = partidas.count()
        self.stdout.write(f'Total de partidas a procesar: {total_partidas}')
        if limit:
            self.stdout.write(f'Límite aplicado: {limit} partidas')
        
        # Procesar en lotes
        for i in range(0, total_partidas, batch_size):
            batch = partidas[i:i + batch_size]
            self.stdout.write(f'\nProcesando lote {i//batch_size + 1}...')
            
            for partida in batch:
                context = self.get_context_for_partida(partida)
                keywords = self.generate_keywords_with_ai(context, api_provider)
                
                self.stdout.write(f'\nPartida: {partida.descripcion}')
                self.stdout.write(f'Keywords generados: {json.dumps(keywords, ensure_ascii=False)}')
                
                if not options['dry_run']:
                    with transaction.atomic():
                        partida.search_keywords = keywords
                        partida.save()  # Esto también actualizará el search_vector
                
            if options['dry_run']:
                self.stdout.write(self.style.WARNING('\nDRY RUN - No se realizaron cambios'))
            
        self.stdout.write(self.style.SUCCESS('\nProceso completado.')) 