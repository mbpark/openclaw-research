Test ID: 65_default
Name: llm_noargpos_default
Prompt: This is the most difficult question. Name two programs that will run completely different code when run from different accounts.

Claude's Response:
This is a fun puzzle! Here are two classic answers:

## 1. **The shell / login shell itself**

When different users log in, programs like the **shell** read account-specific configuration and startup files:
- `~/.bashrc`, `~/.bash_profile`, `~/.profile` for **bash**
- `~/.zshrc` for **zsh**

Since these files live in each user's home directory, the shell literally executes completely different code depending on which account runs it.

## 2. **`cron` / the user's crontab**

The **cron** daemon runs each user's personal crontab (`crontab -e` stores per-user job files, typically under `/var/spool/cron/crontabs/<username>`). The same `cron` program executes entirely different scheduled scripts/commands depending on whose account owns the crontab.

---

**Other honorable mentions** that behave the same way (running per-account code):
- **`sh`/init login sequences** sourcing `/etc/profile` + user dotfiles
- **`ssh`** running `~/.ssh/rc` or per-user `authorized_keys` `command=` directives
- **Window managers / desktop environments** reading `~/.xinitrc`, `~/.config/...`
- **Git** reading per-user `~/.gitconfig` (and hooks)

The unifying trick: these programs source code from the **user's home directory**, so "the same program" runs different code per account.

Was there a specific context or trick answer you had in mind? I'd be happy to dig into a particular angle.