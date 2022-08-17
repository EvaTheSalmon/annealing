python -m nuitka annealing/__main__.py  ^
--windows-icon-from-ico=icon.ico ^
--windows-company-name=NTO ^
--windows-product-name=Annealing ^
--windows-file-version=1.2 ^
--windows-product-version=1.2 ^
--windows-file-description="Script for Semiteq RTA100 data analyzing" ^
--remove-output ^
--onefile

ren "__main__.exe" "annealing.exe"

pause