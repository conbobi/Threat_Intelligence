import requests
import json
from config import Config

def scan_url_with_google(url):
    """
    Kiểm tra URL với Google Safe Browsing API.
    Trả về dict:
    {
        'error': None hoặc thông báo lỗi,
        'risk_score': 0 (an toàn) hoặc 1 (nguy hiểm),
        'message': str mô tả kết quả,
        'threat_type': str loại nguy hiểm nếu có
    }
    """
    api_key = Config.GOOGLE_SAFE_BROWSING_KEY
    if not api_key:
        return {
            'error': 'Google Safe Browsing API key not configured',
            'risk_score': 0,
            'message': 'Không thể kiểm tra Google Safe Browsing do thiếu API key.'
        }

    endpoint = 'https://safebrowsing.googleapis.com/v4/threatMatches:find'
    params = {'key': api_key}

    payload = {
        'client': {
            'clientId': 'your-company-name',      # Có thể đặt tên app của bạn
            'clientVersion': '1.0.0'
        },
        'threatInfo': {
            'threatTypes': [
                'MALWARE', 'SOCIAL_ENGINEERING', 'UNWANTED_SOFTWARE',
                'POTENTIALLY_HARMFUL_APPLICATION', 'THREAT_TYPE_UNSPECIFIED'
            ],
            'platformTypes': ['ANY_PLATFORM'],
            'threatEntryTypes': ['URL'],
            'threatEntries': [{'url': url}]
        }
    }

    try:
        response = requests.post(endpoint, params=params, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'matches' in data and data['matches']:
            match = data['matches'][0]
            threat_type = match.get('threatType', 'UNKNOWN')
            return {
                'error': None,
                'risk_score': 1,
                'message': f'Phát hiện nguy hiểm: {threat_type}',
                'threat_type': threat_type
            }
        else:
            return {
                'error': None,
                'risk_score': 0,
                'message': 'An toàn, không phát hiện nguy hiểm.',
                'threat_type': None
            }
    except requests.exceptions.RequestException as e:
        return {
            'error': str(e),
            'risk_score': 0,
            'message': 'Lỗi khi gọi Google Safe Browsing API.',
            'threat_type': None
        }
    except json.JSONDecodeError:
        return {
            'error': 'Invalid JSON response from Google Safe Browsing',
            'risk_score': 0,
            'message': 'Phản hồi từ Google không hợp lệ.',
            'threat_type': None
        }