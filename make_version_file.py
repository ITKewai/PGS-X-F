# make_version_file.py
from pathlib import Path
from main import __version__, __pgs_version__, __author__, __company__, __product__, __copyright__

# costruisco tuple (major, minor, patch, build)
ver_tuple = tuple(map(int, __version__.split(".")))
pgs_ver_tuple = tuple(map(int, __pgs_version__.split(".")))
while len(ver_tuple) < 4:  # PyInstaller vuole sempre 4 campi
    ver_tuple += (0,)

content = f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={ver_tuple},
    prodvers={pgs_ver_tuple},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [
          StringStruct('CompanyName', '{__company__}'),
          StringStruct('FileDescription', '{__product__}'),
          StringStruct('FileVersion', '{__version__}'),
          StringStruct('InternalName', '{__product__}'),
          StringStruct('OriginalFilename', '{__product__}.exe'),
          StringStruct('ProductName', '{__product__}'),
          StringStruct('ProductVersion', '{__version__}'),
          StringStruct('LegalCopyright', '{__copyright__}')
        ]
      )
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)"""

Path("version_info.txt").write_text(content, encoding="utf-8")
print("Creato version_info.txt con version =", __version__)

