import json
from typing import Dict, Set

class ConfigValidationError(Exception):
    """Raised when config files don't match the expected schema"""
    pass

def _get_key_diff_message(expected: Set[str], actual: Set[str]) -> str:
    missing = expected - actual
    extra = actual - expected
    msg = []
    if missing:
        msg.append(f"Keys expected but not found: {', '.join(missing)}")
    if extra:
        msg.append(f"Keys found but not expected: {', '.join(extra)}")
    return " | ".join(msg)

def validate_configs(slack_config: Dict, config: Dict) -> None:
    # Load sample configs to validate against
    with open('slack_config_sample.json', 'r') as file:
        slack_config_sample = json.load(file)
    with open('config.json', 'r') as file:
        config_sample = json.load(file)

    # Validate slack_config.json schema
    expected_keys = set(slack_config_sample.keys())
    actual_keys = set(slack_config.keys())
    if expected_keys != actual_keys:
        raise ConfigValidationError(f"slack_config.json has different keys than slack_config_sample.json: {_get_key_diff_message(expected_keys, actual_keys)}")
    
    expected_app_info_keys = set(slack_config_sample['slack_app_info'].keys())
    actual_app_info_keys = set(slack_config['slack_app_info'].keys())
    if expected_app_info_keys != actual_app_info_keys:
        raise ConfigValidationError(f"slack_app_info structure differs: {_get_key_diff_message(expected_app_info_keys, actual_app_info_keys)}")

    expected_app_keys = {'slack_token', 'slack_member_id'}
    for i, agent_app in enumerate(slack_config['slack_app_info']['agent_apps']):
        actual_app_keys = set(agent_app.keys())
        if actual_app_keys != expected_app_keys:
            raise ConfigValidationError(f"agent_app at index {i} has incorrect keys: {_get_key_diff_message(expected_app_keys, actual_app_keys)}")

    world_app_keys = set(slack_config['slack_app_info']['world_app'].keys())
    if world_app_keys != expected_app_keys:
        raise ConfigValidationError(f"world_app has incorrect keys: {_get_key_diff_message(expected_app_keys, world_app_keys)}")

    expected_human_keys = {'slack_member_id', 'name', 'expertise'}
    for i, human in enumerate(slack_config['humans']):
        actual_human_keys = set(human.keys())
        if actual_human_keys != expected_human_keys:
            raise ConfigValidationError(f"human at index {i} has incorrect keys: {_get_key_diff_message(expected_human_keys, actual_human_keys)}")

    # Validate config.json schema
    expected_config_keys = set(config_sample.keys())
    actual_config_keys = set(config.keys())
    if expected_config_keys != actual_config_keys:
        raise ConfigValidationError(f"config.json has different keys than config_sample.json: {_get_key_diff_message(expected_config_keys, actual_config_keys)}") 