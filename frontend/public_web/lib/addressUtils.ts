/**
 * Utility functions for composing and formatting shipping addresses
 */

/**
 * Compose Miami warehouse shipping address with client identification
 *
 * Format:
 * {Client Name} - {Client Code}
 * {Consolidator Address}
 *
 * @param clientName - Full name of the client
 * @param clientCode - Client code (e.g., "CLI-001234")
 * @param consolidatorAddress - Miami warehouse address from system parameters
 * @returns Formatted shipping address string
 */
export function composeShippingAddress(
  clientName: string,
  clientCode: string,
  consolidatorAddress: string
): string {
  return `${clientName} - ${clientCode}\n${consolidatorAddress}`;
}

/**
 * Copy text to clipboard
 *
 * @param text - Text to copy
 * @returns Promise that resolves when text is copied
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      const success = document.execCommand('copy');
      textArea.remove();
      return success;
    }
  } catch (error) {
    console.error('Failed to copy to clipboard:', error);
    return false;
  }
}

/**
 * Format WhatsApp number for wa.me link
 *
 * @param whatsappNumber - WhatsApp number with country code (e.g., "+504 9548 8535")
 * @returns Formatted number for WhatsApp URL (e.g., "50495488535")
 */
export function formatWhatsAppNumber(whatsappNumber: string): string {
  return whatsappNumber.replace(/[^0-9]/g, '');
}

/**
 * Generate Google Maps search URL for an address
 *
 * @param address - Address to search for
 * @returns Google Maps URL
 */
export function getGoogleMapsUrl(address: string): string {
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address)}`;
}

/**
 * Generate Waze navigation URL for an address
 *
 * @param address - Address to navigate to
 * @returns Waze URL
 */
export function getWazeUrl(address: string): string {
  return `https://waze.com/ul?q=${encodeURIComponent(address)}`;
}

/**
 * Generate WhatsApp chat URL
 *
 * @param whatsappNumber - WhatsApp number with country code
 * @param message - Optional pre-filled message
 * @returns WhatsApp URL
 */
export function getWhatsAppUrl(whatsappNumber: string, message?: string): string {
  const formattedNumber = formatWhatsAppNumber(whatsappNumber);
  const baseUrl = `https://wa.me/${formattedNumber}`;

  if (message) {
    return `${baseUrl}?text=${encodeURIComponent(message)}`;
  }

  return baseUrl;
}
