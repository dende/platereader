# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['dende\\platereader\\__main__.py'],
             binaries=[],
             datas=[('dende/platereader/platereader.ico', '.')],
             hiddenimports=['openpyxl', '_openpyxl', 'pandas', 'pandas.plotting', 'pandas.plotting._matplotlib'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='platereader',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          icon='dende\\platereader\\platereader.ico')
