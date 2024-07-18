import shlex
import subprocess
import sys

from GlyphsApp import Glyphs, GSGlyphsInfo, GSScriptingHandler
from io import StringIO
from pathlib import Path


# From https://github.com/googlefonts/fontc-export-plugin/blob/main/fontcExport.glyphsFileFormat/Contents/Resources/plugin.py#L226-L237


def run_subprocess_in_macro_window(
    command,
    check=False,
    show_window=False,
    capture_output=False,
    echo=True,
):
    """Wrapper for subprocess.run that writes in real time to Macro output window"""

    if show_window:
        Glyphs.showMacroWindow()

    if echo:
        # echo command
        print(f"$ {' '.join(shlex.quote(str(arg)) for arg in command)}")

    # Start the subprocess asynchronously and redirect output to a pipe
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Redirect stderr to stdout
        encoding="utf-8",
        text=True,
        bufsize=1,  # Line-buffered
    )

    # Read the output line by line and write to Glyphs.app's Macro output window
    output = StringIO() if capture_output else None
    while process.poll() is None:
        for line in process.stdout:
            sys.stdout.write(line)
            if output is not None:
                output.write(line)

    returncode = process.wait()

    if check and returncode != 0:
        # Raise an exception if the process returned an error code
        raise subprocess.CalledProcessError(
            returncode, process.args, process.stdout, process.stderr
        )

    if capture_output:
        return subprocess.CompletedProcess(
            process.args, returncode, output.getvalue(), ""
        )

    return subprocess.CompletedProcess(process.args, returncode, None, None)


def installViaPip(package_name: str) -> None:
    scriptingHandler = GSScriptingHandler.sharedHandler()
    glyphsPythonPath = Path(scriptingHandler.currentPythonPath()) / "bin" / "python3"
    targetPath = (
        Path(GSGlyphsInfo.applicationSupportPath()) / "Scripts" / "site-packages"
    )

    installCommand = [
        glyphsPythonPath,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--target",
        targetPath,
        package_name,
    ]
    run_subprocess_in_macro_window(installCommand, check=True)
