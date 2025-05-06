{ pkgs }: {
  deps = [
    pkgs.python39
    pkgs.python39Packages.pip
    pkgs.python39Packages.flask
    pkgs.python39Packages.pillow
    pkgs.python39Packages.requests
  ];
}