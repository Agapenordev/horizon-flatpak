# Horizon Flatpak

Unofficial [Flatpak](https://flatpak.org/) packaging for [Horizon](https://github.com/horizon-rust/horizon), the unofficial Minecraft: Java Edition rewrite in Rust.

This repository packages Horizon's official Linux launcher with a restrictive sandbox and a pinned SHA-256 checksum. It is not affiliated with or endorsed by the Horizon project, Mojang, or Microsoft.

## Install

The package supports **Linux x86-64** and uses the Freedesktop 25.08 runtime.

```bash
flatpak install --user flathub org.freedesktop.Platform//25.08
flatpak install --user https://agapenordev.github.io/horizon-flatpak/dev.playhorizon.Horizon.flatpakref
```

Start Horizon from your application menu or run:

```bash
flatpak run dev.playhorizon.Horizon
```

You need your own copy of Minecraft: Java Edition 26.3. Follow Horizon's [installation guide](https://playhorizon.dev/docs/install) to prepare the game.

## Sandbox permissions

The launcher has access only to the features it needs:

- Network access for downloads and multiplayer.
- Wayland or X11, GPU, and PulseAudio access for the game.
- **Read-only** access to `~/.minecraft` for your existing installation and Java runtime.
- Read/write access to its own Flatpak data directory.

It has no general access to your home directory, documents, SSH keys, or other applications' data. Its files are stored under:

```text
~/.var/app/dev.playhorizon.Horizon/
```

Back up this directory before uninstalling if you want to keep your Horizon worlds and settings. A nonstandard Minecraft directory can be granted explicitly, for example:

```bash
flatpak override --user --filesystem=/path/to/minecraft:ro dev.playhorizon.Horizon
```

## Security scope

Flatpak limits what the application can access; it does not prove that Horizon is safe. This package uses Horizon's prebuilt launcher rather than compiling it from source, and the launcher still downloads executable game updates inside the sandbox. The upstream archive is verified against the SHA-256 checksum recorded in the manifest.

The Flatpak installation under `/app` is read-only, so the launcher's self-updater may not work. Update this package to upgrade the launcher itself.

## Build from source packaging

Install the Flatpak build tool, then build and install locally:

```bash
flatpak install --user flathub org.flatpak.Builder
flatpak run org.flatpak.Builder \
  --force-clean --user --install-deps-from=flathub \
  --repo=repo --install builddir dev.playhorizon.Horizon.yml
```

Create a single-file bundle:

```bash
flatpak build-bundle repo horizon-launcher.flatpak dev.playhorizon.Horizon
```

To update the package manually, replace the launcher URL and SHA-256 checksum in `dev.playhorizon.Horizon.yml`, then add the corresponding release to `dev.playhorizon.Horizon.metainfo.xml`.

## Automatic releases and updates

A [GitHub Actions workflow](.github/workflows/update-launcher.yml) checks for a new upstream launcher every six hours. When one is available, it verifies and pins the new archive, builds the Flatpak, commits the manifest changes, and publishes a GitHub release. A [second workflow](.github/workflows/publish-repository.yml) publishes the corresponding Flatpak repository to GitHub Pages. Both workflows can also be started manually from the repository's Actions page.

After installing through the `.flatpakref`, update Horizon with:

```bash
flatpak update --user dev.playhorizon.Horizon
```

To switch an existing standalone-bundle installation to repository updates, uninstall and reinstall it through the `.flatpakref`. This preserves Horizon's application data; do not add `--delete-data`:

```bash
flatpak uninstall --user dev.playhorizon.Horizon
flatpak install --user https://agapenordev.github.io/horizon-flatpak/dev.playhorizon.Horizon.flatpakref
```

## Uninstall

```bash
flatpak uninstall --user dev.playhorizon.Horizon
```

Add `--delete-data` only if you also want to delete Horizon's sandboxed worlds and settings.

## License

The packaging files are available under the [MIT License](LICENSE). Horizon and its dependencies retain their own licenses; the relevant upstream notices are included in the packaged application.
