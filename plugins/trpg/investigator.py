from . import dice
from essentials.libraries import asset

_assets = asset.Asset('trpg')


def random_investigator() -> dict[str, int]:
    return {
        'str': dice.dice_expression('3d6*5')[0],
        'con': dice.dice_expression('3d6*5')[0],
        'siz': dice.dice_expression('(2d6+6)*5')[0],
        'dex': dice.dice_expression('3d6*5')[0],
        'app': dice.dice_expression('3d6*5')[0],
        'int': dice.dice_expression('(2d6+6)*5')[0],
        'pow': dice.dice_expression('3d6*5')[0],
        'edu': dice.dice_expression('(2d6+6)*5')[0],
        'luck': dice.dice_expression('3d6*5')[0],
    }


def get_property_name(key: str) -> str:
    key = key.lower()
    if key in _assets['noun']:
        return _assets['noun'][key]
    return ''
