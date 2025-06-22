from typing import Dict


def get_config(self) -> Dict:
    """Get current configuration"""
    return self._config.copy()


def sanitize_config(self, config: Dict) -> Dict:
    """Remove sensitive information from config"""
    sanitized = config.copy()

    # Remove sensitive keys (passwords, tokens, etc.)
    sensitive_keys = ['password', 'token', 'secret', 'key', 'api_key']

    def remove_sensitive(obj):
        if isinstance(obj, dict):
            return {k: remove_sensitive(v) if k.lower() not in sensitive_keys else "***"
                    for k, v in obj.items()}
        elif isinstance(obj, list):
            return [remove_sensitive(item) for item in obj]
        return obj

    return remove_sensitive(sanitized)
