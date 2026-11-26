# nerdcules

A directory of my public projects: tools for AI coding assistants, and desktop apps for
[Omarchy](https://omarchy.org) (Arch Linux + Hyprland) in C++ and Qt Quick.

> **Who made these.** The ideas are mine: what each project is for, what it should do, and how it
> should look. The code and the docs are written by AI, by Claude (Anthropic) working in
> [Claude Code](https://claude.com/claude-code). Each section below says so for its project, with
> the share of commits that carry Claude's `Co-Authored-By` line.

| Project | What it is | Language | Release |
|---|---|---|---|
| [CodeGraph](#codegraph) | Code graph MCP server: who calls this, what breaks if I change it, which tests guard it | C# | [![release](https://img.shields.io/github/v/release/nerdcules/CodeGraph?include_prereleases&label=)](https://github.com/nerdcules/CodeGraph/releases) |
| [sankofa](#sankofa) | Shared memory and file locks for many AI coding sessions on one codebase | C# | [![release](https://img.shields.io/github/v/release/nerdcules/sankofa?include_prereleases&label=)](https://github.com/nerdcules/sankofa/releases) |
| [Fathom](#fathom) | A Windows-inspired desktop layer for Omarchy, built for Docker, .NET and AI work | QML | [![release](https://img.shields.io/github/v/release/nerdcules/fathom?include_prereleases&label=)](https://github.com/nerdcules/fathom/releases) |
| [o-rdp](#o-rdp) | Finds the PCs with Remote Desktop on your network and connects to them | C++ / Qt Quick | – |
| [Snoopy](#snoopy) | What each app on a connected Android phone reads, and where it connects | C++ / Qt Quick | – |
| [Ward](#ward) | Which published CVEs affect this machine, and which of them matter here | C++ / Qt Quick | [![release](https://img.shields.io/github/v/release/nerdcules/ward?include_prereleases&label=)](https://github.com/nerdcules/ward/releases) |

Keeping them up to date, with pre-releases to test and a way back: [Updates](#updates).

---

## CodeGraph

**[github.com/nerdcules/CodeGraph](https://github.com/nerdcules/CodeGraph)**  
Idea: mine · Written by: Claude, in Claude Code · 78 of 100 commits co-authored by Claude (counted 18 Nov 2026)

Gives your AI coding assistant the compiler's answers: who calls this, what breaks if I change it,
which tests guard it. It reads a codebase with its compiler (C#, TypeScript and Angular, Java, Go,
Rust, Python), stores what it finds as a graph, and serves that graph to the assistant as MCP tools.
It sets itself up for Claude Code, GitHub Copilot, Codex, Cursor, the Gemini CLI, and the Roo Code,
Kilo Code and Continue extensions.

[![A real Claude Code session replayed from its transcript: asked what breaks if GraphStore.Replace changes, Claude calls four codegraph tools and answers](images/codegraph-session.gif)](https://github.com/nerdcules/CodeGraph)

*A real Claude Code session (14 November 2026), replayed from its transcript. With CodeGraph the
assistant answered in 42 s with four codegraph calls; without it, 87 s and eight shell commands.
Details and the later run-time check are in the
[CodeGraph README](https://github.com/nerdcules/CodeGraph#readme).*

<table><tr>
<td width="50%"><img src="images/codegraph-graph-view.png" alt="The code graph opened as an Obsidian vault, in graph view"></td>
<td width="50%"><img src="images/codegraph-architecture.svg" alt="Architecture: extractors write graph.db, the MCP server and the codegraph CLI read it, the live daemon keeps it current"></td>
</tr><tr>
<td>The graph as an Obsidian vault</td>
<td>Extractors write the graph, the MCP server reads it, a daemon keeps it current</td>
</tr></table>

## sankofa

**[github.com/nerdcules/sankofa](https://github.com/nerdcules/sankofa)**  
Idea: mine · Written by: Claude, in Claude Code · 51 of 57 commits co-authored by Claude (counted 18 Nov 2026)

*Sankofa* (Akan): "go back and fetch it." One small ledger that every AI coding session, subagent,
client and machine goes back to: what was done, what is open, who is working on which files, what to
do next. With Claude Code every edit is leased before it happens, so a second session touching the
same files is refused by name. Linux, macOS and Windows share one ledger.

<table><tr>
<td width="50%"><img src="images/sankofa-radar.png" alt="The sankofa dashboard: what waits on you, what is open, who holds what, as a radar by age"></td>
<td width="50%"><img src="images/sankofa-map.png" alt="The sankofa device map: every device writing to the ledger"></td>
</tr><tr>
<td>Radar: what waits on you, what is open, who holds what</td>
<td>Device map: every machine writing to the ledger</td>
</tr></table>

## Fathom

**[github.com/nerdcules/fathom](https://github.com/nerdcules/fathom)**  
Idea: mine · Written by: Claude, in Claude Code · 61 of 61 commits co-authored by Claude (counted 18 Nov 2026)

A futuristic, Windows-inspired desktop layer for Omarchy, built for Docker, .NET and AI work:
a desktop theme with a glassy bar, a Start menu, and the Command Deck, whose pages are the system,
containers, .NET apps and AI agents; Care (updates, failed services, disk); Sentinel (firewall
blocks, sign-ins, new devices on your network, system files); Pulse (a map of what calls what in your
stack, and Claude Code's day); Crumbs (every browser's cookies and the trackers behind them); and
Personalise. Then Alt+Tab with previews, Task view, Snap layouts, Quick settings, a mini-player, mail
notifications and a sign-in screen. Each part installs on its own, `fathom-update` follows its
releases, and its version and build number show in the deck, Start, Quick settings and the sign-in
screen.

**[0.2.0](https://github.com/nerdcules/fathom/releases/tag/v0.2.0)** (18 November 2026) adds the
laptop side of Fathom for Android, an Android home screen (private for now): pairing by QR code,
alerts the phone can act on, Sankofa's ledgers, the phone's own health kept on the laptop, and Ask
Claude, where Claude Code on the laptop explains what the health rules found. Checked in an
Omarchy 4.5.0-3 VM: 26 passed, 0 failed.

![Fathom desktop](images/fathom-desktop.png)

[![Personalise changing Fathom's accent and corners, from the promo](images/fathom-promo.gif)](https://github.com/nerdcules/fathom#promo)

*From the 92.83-second promo (17 November 2026); the tour is in the
[Fathom README](https://github.com/nerdcules/fathom#promo).*

<table><tr>
<td width="50%"><img src="images/fathom-start.jpg" alt="Fathom Start menu"></td>
<td width="50%"><img src="images/fathom-deck.jpg" alt="Fathom Command Deck"></td>
</tr><tr>
<td>Start menu</td>
<td>Command Deck</td>
</tr><tr>
<td width="50%"><img src="images/fathom-care.jpg" alt="Fathom Care"></td>
<td width="50%"><img src="images/fathom-crumbs.jpg" alt="Crumbs, showing made-up browsing"></td>
</tr><tr>
<td>Care</td>
<td>Crumbs (made-up browsing)</td>
</tr></table>

## o-rdp

**[github.com/nerdcules/o-rdp](https://github.com/nerdcules/o-rdp)**  
Idea: mine · Written by: Claude, in Claude Code · 3 of 3 commits co-authored by Claude (counted 18 Nov 2026)

Finds the PCs with Remote Desktop on your local network and connects to them with FreeRDP. It scans
the subnet of the default route for port 3389, names each PC (NetBIOS, reverse DNS, then Avahi),
keeps passwords in the GNOME keyring if you ask it to, and says what went wrong when a connection
fails. Keyboard-driven.

![o-rdp listing the PCs on the network (made-up hosts)](images/o-rdp.png)

## Snoopy

**[github.com/nerdcules/snoopy](https://github.com/nerdcules/snoopy)**  
Idea: mine · Written by: Claude, in Claude Code · 27 of 29 commits co-authored by Claude (counted 18 Nov 2026)

For an Android phone plugged into this computer, shows what each app recently read (location,
camera, microphone, contacts, photos, clipboard and more) and where it is connected: the address,
its reverse DNS name, the port, and the names the phone looked up. It reads the phone over adb;
nothing is installed on the phone and nothing is decrypted.

<table><tr>
<td width="50%"><img src="images/snoopy.png" alt="Snoopy showing which apps read what, and where they connect (made-up data)"></td>
<td width="50%"><img src="images/snoopy-watch.png" alt="Snoopy's Watch page (made-up apps)"></td>
</tr><tr>
<td>Apps, what they read, where they connect</td>
<td>The Watch page</td>
</tr></table>


## Ward

**[github.com/nerdcules/ward](https://github.com/nerdcules/ward)**  
Idea: mine · Written by: Claude, in Claude Code · 1 of 1 commits co-authored by Claude (counted 20 Nov 2026)

Matches every installed pacman package, and the kernel, against CVE.org's records, Arch's
security tracker, CISA's list of exploited vulnerabilities and kernel.org's maintained branches.
It works out what the machine actually uses (running services, loaded libraries, listening
sockets, which kernel modules are loaded) and has Claude Code, with no tools, judge what is left:
does it apply here, and how soon does it matter. A daily check, once you turn it on, alerts you when something needs
you; fixes run in a terminal only after you confirm.

![Ward listing the packages a CVE matches, with triage's verdicts (made-up data)](images/ward.png)

## Updates

`nerdcules-update` updates the apps above that run on this computer (o-rdp, Snoopy, Ward, Fathom,
sankofa and CodeGraph) and Imbizo, from their own repositories, and goes back when an update doesn't work out.
`bin/install-update` links it into `~/.local/bin`.

```bash
nerdcules-update                                 # each app: installed, channel, newest
nerdcules-update apply o-rdp                     # install the newest on o-rdp's channel
nerdcules-update rollback o-rdp                  # back to the version before
nerdcules-update install o-rdp v0.2.0-rc.1       # any tag (or main), to test it or go further back
nerdcules-update versions o-rdp                  # the tags published, and the builds kept here
nerdcules-update channel o-rdp prerelease        # stable (default) | prerelease | main
```

Versions are git tags named for [semantic versions](https://semver.org): `v1.2.0` is a release,
`v1.2.0-rc.1` a pre-release of it. The **stable** channel offers releases only; **prerelease**
offers whichever tag is newest, so it moves on from `v1.2.0-rc.1` to `v1.2.0` when that is
tagged; **main** follows every commit. A pre-release published on GitHub is marked as one
(`gh release create v1.2.0-rc.1 --prerelease`), so GitHub's "latest" is never a pre-release.

Nothing runs on its own. What goes online: `git` to each app's own GitHub repository (check,
versions, apply, install), sankofa's and CodeGraph's release downloads from GitHub, and pacman to your mirrors
when a build or an install needs a package you don't have. How each app installs is in
[apps.json](apps.json):

| Kind | Apps | Update | Rollback |
|---|---|---|---|
| `makepkg` | o-rdp, Snoopy, Ward, Imbizo | clones the repo into `~/.local/share/nerdcules-update/<app>/src`, builds the tag's Arch package with `pkgver` set from the tag (`v0.2.0-rc.1` becomes `0.2.0rc.1`, which pacman puts before `0.2.0`; `main` becomes `0.1.0.r5.gabc1234`), installs it with `sudo pacman -U` | reinstalls the earlier package, kept next to the clone, without building |
| `fathom-update` | Fathom | Fathom's own updater; its channels are `releases`, `prereleases`, `main` | `fathom-update rollback` |
| `release-tarball` | sankofa | downloads the tag's release tarball, unpacks it beside the earlier ones in `~/.local/share/sankofa`, points `current` at it and runs its `install.sh` | points `current` back and runs that version's `install.sh` |
| `install-script` | CodeGraph | downloads the app's own install script at the tag and runs it with the tag (`install.sh --version v1.6.0 --yes --no-vscode`); the app's `VERSION` file (`~/.codegraph/bin/VERSION`) says what is installed | runs the earlier tag's install script again, so it downloads that release again |

sankofa run from a clone of your own (its command a link into a git checkout, as its `./install.sh`
run from the clone leaves it) is left alone: `nerdcules-update` says to `git pull` there instead. o-rdp, Snoopy, Ward and Imbizo
installed with their own `bin/install` are ordinary packages, and an update replaces them.
Fathom always updates the clone it was installed from, as `fathom-update` does.
CodeGraph keeps one version in `~/.codegraph/bin`; its install script stops when an assistant session
is running `codegraph-mcp` from there, so close those sessions first. It does not update the VS Code
extension (`--no-vscode`); re-run CodeGraph's `install.sh --vscode` for that.

A new app joins with an entry in `apps.json` (its repo, its kind, and for `makepkg` its package
name and PKGBUILD folder; for `install-script` the script's URL, its arguments and the VERSION file), and by tagging its releases `vMAJOR.MINOR.PATCH`, pre-releases
`vMAJOR.MINOR.PATCH-rc.N`. Tests: `python3 -m unittest tests.test_update` (real git repos and a
real `makepkg` build of a stand-in package; a stand-in pacman, nothing installed).

---

<sub>Ideas: mine. Code and writing: Claude, in Claude Code. Commit counts come from each repo's
history on GitHub on the date given beside each; a commit without the trailer is not a claim either way.
Screenshots are copies of the ones in each project's own repo; `bin/refresh-images` fetches
them again (sources in [images/SOURCES](images/SOURCES)).</sub>
