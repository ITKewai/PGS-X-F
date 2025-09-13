# make_version_file.py
from pathlib import Path
import main  # importa __version__, __company__, __product__, __copyright__

# costruisco tuple (major, minor, patch, build)
ver_tuple = tuple(map(int, main.__version__.split(".")))
while len(ver_tuple) < 4:  # PyInstaller vuole sempre 4 campi
    ver_tuple += (0,)

content = f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={ver_tuple},
    prodvers={ver_tuple},
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
          StringStruct('CompanyName', '{main.__company__}'),
          StringStruct('FileDescription', '{main.__product__}'),
          StringStruct('FileVersion', '{main.__version__}'),
          StringStruct('InternalName', '{main.__product__}'),
          StringStruct('OriginalFilename', '{main.__product__}.exe'),
          StringStruct('ProductName', '{main.__product__}'),
          StringStruct('ProductVersion', '{main.__version__}'),
          StringStruct('LegalCopyright', '{main.__copyright__}')
        ]
      )
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)"""

Path("version_info.txt").write_text(content, encoding="utf-8")
print("✅ Creato version_info.txt con version =", main.__version__)
