{ pkgs }: {
  deps = [
    pkgs.ffmpeg
    pkgs.libcairo
    pkgs.pango
    pkgs.pkg-config
    pkgs.python311Full
    pkgs.python311Packages.pip
    pkgs.python311Packages.setuptools
    pkgs.python311Packages.wheel
    pkgs.python311Packages.uvicorn
    pkgs.python311Packages.fastapi
    pkgs.python311Packages.manim
    pkgs.texlive.combined.scheme-full
  ];
}