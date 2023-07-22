from essentials.libraries import asset, storage

trpg_assets = asset.Asset('trpg')
trpg_data = storage.PersistentData('trpg')

__all__ = ['trpg_assets', 'trpg_data']
