{
  description = "Development shell for platform engineering learning labs";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { nixpkgs, ... }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
        "x86_64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in {
      devShells = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
        in {
          default = pkgs.mkShell {
            packages = [
              pkgs.python3
              pkgs.nodejs
              pkgs.nginx
            ];

            shellHook = ''
              echo "learning-platform-engineering dev shell"
              echo "Try: python3 projects/network-protocol-lab/test_protocol.py"
              echo "Try: python3 projects/nginx-reverse-proxy/check_config.py"
              echo "Try: node projects/realtime-transport-fallback/transport.test.mjs"
            '';
          };
        });
    };
}
