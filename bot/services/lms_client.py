"""
LMS API client for the bot.
Handles all communication with the backend.
"""

import requests
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config


class LMSClient:
    """Client for LMS backend API."""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = (base_url or Config.LMS_API_BASE_URL).rstrip('/')
        self.api_key = api_key or Config.LMS_API_KEY
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def _request(self, method: str, path: str, **kwargs):
        """Make HTTP request to backend."""
        url = f"{self.base_url}{path}"
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            return {'error': f'Connection refused to {self.base_url}'}
        except requests.exceptions.Timeout:
            return {'error': 'Request timeout'}
        except requests.exceptions.HTTPError as e:
            return {'error': f'HTTP {response.status_code}: {response.text[:100]}'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_items(self):
        """Get all items (labs and tasks)."""
        return self._request('GET', '/items/')
    
    def get_learners(self):
        """Get list of enrolled students."""
        return self._request('GET', '/learners/')
    
    def get_scores(self, lab: str):
        """Get score distribution for a lab."""
        return self._request('GET', f'/analytics/scores?lab={lab}')
    
    def get_pass_rates(self, lab: str):
        """Get pass rates for a lab."""
        return self._request('GET', f'/analytics/pass-rates?lab={lab}')
    
    def get_timeline(self, lab: str):
        """Get submissions timeline for a lab."""
        return self._request('GET', f'/analytics/timeline?lab={lab}')
    
    def get_groups(self, lab: str):
        """Get per-group performance for a lab."""
        return self._request('GET', f'/analytics/groups?lab={lab}')
    
    def get_top_learners(self, lab: str, limit: int = 5):
        """Get top N learners for a lab."""
        return self._request('GET', f'/analytics/top-learners?lab={lab}&limit={limit}')
    
    def get_completion_rate(self, lab: str):
        """Get completion rate for a lab."""
        return self._request('GET', f'/analytics/completion-rate?lab={lab}')
    
    def trigger_sync(self):
        """Trigger ETL sync."""
        return self._request('POST', '/pipeline/sync', json={})
