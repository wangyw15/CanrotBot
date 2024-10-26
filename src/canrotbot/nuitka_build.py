# nuitka-project: --include-package=nonebot.drivers.fastapi
# nuitka-project: --include-package=nonebot.drivers.httpx
# nuitka-project: --include-package=nonebot.drivers.websockets
# nuitka-project: --include-package=nonebot_plugin_apscheduler
# nuitka-project: --include-package=nonebot_plugin_alconna
# nuitka-project-if: {OS} == "Windows":
#    nuitka-project: --output-filename=canrotbot.exe
# nuitka-project-else:
#    nuitka-project: --output-filename=canrotbot
# nuitka-project-if: {OS} in ("Windows", "Linux", "Darwin", "FreeBSD"):
#    nuitka-project: --onefile
# nuitka-project-else:
#    nuitka-project: --standalone

if __name__ == "__main__":
    import canrotbot
    canrotbot.run()
