from django.db import connection


def check_field_exists():
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'MiCasillero_partidaarancelaria' 
            AND column_name = 'search_vector';
        """
        )
        result = cursor.fetchone()

    if result:
        print(
            f"El campo 'search_vector' SÍ existe en la tabla MiCasillero_partidaarancelaria"
        )
    else:
        print(
            f"El campo 'search_vector' NO existe en la tabla MiCasillero_partidaarancelaria"
        )


if __name__ == "__main__":
    check_field_exists()
