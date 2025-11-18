import requests
import json
import logging
from config import API_ENDPOINTS, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

class CardAPIClient:
    def __init__(self):
        self.endpoints = API_ENDPOINTS
    
    def check_card(self, card_data: str, gateway: str = 'stripe1') -> dict:
        """Check card using specified gateway"""
        try:
            if gateway not in self.endpoints:
                return {
                    'success': False,
                    'error': f"Gateway not supported: {gateway}"
                }
            
            url = f"{self.endpoints[gateway]}{card_data}"
            logger.info(f"Calling API: {url}")
            
            response = requests.get(url, timeout=REQUEST_TIMEOUT, verify=False)
            
            if response.status_code == 200:
                try:
                    response_data = json.loads(response.text)
                    return {
                        'success': True,
                        'status_code': response.status_code,
                        'data': response_data,
                        'gateway': gateway,
                        'error': None
                    }
                except json.JSONDecodeError:
                    return {
                        'success': True,
                        'status_code': response.status_code,
                        'data': {'response': response.text},
                        'gateway': gateway,
                        'error': None
                    }
            else:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'data': None,
                    'gateway': gateway,
                    'error': f"HTTP Error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'status_code': None,
                'data': None,
                'gateway': gateway,
                'error': str(e)
            }
    
    def check_crunchyroll(self, credentials: str) -> dict:
        """Check Crunchyroll account"""
        try:
            url = f"{self.endpoints['crunchyroll']}{credentials}"
            logger.info(f"Checking Crunchyroll: {url}")
            
            response = requests.get(url, timeout=REQUEST_TIMEOUT, verify=False)
            
            if response.status_code == 200:
                try:
                    response_data = json.loads(response.text)
                    return {
                        'success': True,
                        'status_code': response.status_code,
                        'data': response_data,
                        'gateway': 'crunchyroll',
                        'error': None
                    }
                except json.JSONDecodeError:
                    return {
                        'success': True,
                        'status_code': response.status_code,
                        'data': {'response': response.text},
                        'gateway': 'crunchyroll',
                        'error': None
                    }
            else:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'data': None,
                    'gateway': 'crunchyroll',
                    'error': f"HTTP Error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'status_code': None,
                'data': None,
                'gateway': 'crunchyroll',
                'error': str(e)
            }
    
    def bin_lookup(self, bin_number: str) -> dict:
        """Lookup BIN information"""
        try:
            if len(bin_number) < 6:
                return {
                    'success': False,
                    'error': "BIN must be at least 6 digits"
                }
            
            url = f"{self.endpoints['bin_lookup']}{bin_number}"
            logger.info(f"BIN Lookup: {url}")
            
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                bin_data = response.json()
                return {
                    'success': True,
                    'data': bin_data,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'data': None,
                    'error': f"BIN API Error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'error': str(e)
            }
    
    def generate_cards(self, bin_number: str) -> dict:
        """Generate credit cards"""
        try:
            if len(bin_number) < 6:
                return {
                    'success': False,
                    'error': "BIN must be at least 6 digits"
                }
            
            url = f"{self.endpoints['cc_generator']}{bin_number}"
            logger.info(f"Generate Cards: {url}")
            
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                cards_text = response.text.strip()
                cards_list = [card.strip() for card in cards_text.split('\n') if card.strip()]
                return {
                    'success': True,
                    'data': cards_list,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'data': None,
                    'error': f"Generator API Error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'error': str(e)
            }

api_client = CardAPIClient()