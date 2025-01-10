from typing import Dict, Optional
import requests
import urllib3

class OpnsenseClient:
    def __init__(self, host: str, api_key: str, api_secret: str, verify_ssl: bool = True):
        """
        Initialize OPNsense API client

        Args:
            host: OPNsense host address (e.g., 'https://192.168.1.1')
            api_key: API key from OPNsense
            api_secret: API secret from OPNsense
            verify_ssl: Whether to verify SSL certificate
        """
        self.base_url = f"{host.rstrip('/')}/api"
        self.auth = (api_key, api_secret)
        self.headers = {'Content-Type': 'application/json'}
        self.verify_ssl = verify_ssl

        if not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def get(self, endpoint: str) -> Dict:
        """
        Perform GET request to OPNsense API

        Args:
            endpoint: API endpoint path (e.g., '/dhcpv4/leases/searchLease')

        Returns:
            Dict containing the API response
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(
                url,
                auth=self.auth,
                verify=self.verify_ssl,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error in GET request to {url}: {e}")
            return {"error": str(e)}

    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Perform POST request to OPNsense API

        Args:
            endpoint: API endpoint path
            data: Optional JSON data to send with the request

        Returns:
            Dict containing the API response
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.post(
                url,
                auth=self.auth,
                verify=self.verify_ssl,
                headers=self.headers,
                json=data if data is not None else {}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error in POST request to {url}: {e}")
            return {"error": str(e)}


class OpnsenseApi:
    def __init__(self, client: OpnsenseClient):
        """
        Initialize OPNsense API wrapper

        Args:
            client: OpnsenseClient instance for making HTTP requests
        """
        self.client = client

    def get_dhcp_leases(self) -> Dict:
        """
        Get all DHCP leases from the system

        Returns:
            Dict containing DHCP lease information
        """
        return self.client.get('/dhcpv4/leases/searchLease')

    def get_blocklist_status(self) -> bool:
        """
        Get the current status of DNS blocking

        Returns:
            Boolean indicating if DNS blocking is enabled
        """
        response = self.client.get('/unbound/settings/get')
        return response.get('unbound', {}).get('dnsbl', {}).get('enabled') == "1"

    def toggle_unbound_blocklist(self, enable: bool = True) -> Dict:
        """
        Enable or disable the Unbound DNS blocklist feature

        Args:
            enable: True to enable, False to disable

        Returns:
            Dict: API response
        """
        payload = {
            "unbound": {
                "dnsbl": {
                    "enabled": "1" if enable else "0"  # '1' for enabled, '0' for disabled
                }
            }
        }

        response = self.client.post('/unbound/settings/set', payload)

        # Apply the changes by reconfiguring the service if successful
        if response.get('result') == 'saved':
            self.reconfigure_unbound()

        return response

    def reconfigure_unbound(self) -> Dict:
        """
        Reconfigure the Unbound service to apply changes

        Returns:
            Dict: API response
        """
        return self.client.post('/unbound/service/reconfigure')
