# envault

> A CLI tool for encrypting and managing per-project `.env` files with team-sharing support.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended):

```bash
pipx install envault
```

---

## Usage

```bash
# Initialize envault in your project
envault init

# Encrypt your .env file
envault lock --file .env

# Decrypt and load the environment
envault unlock --file .env.vault

# Share the vault with your team (exports an encrypted bundle)
envault share --out team.vault --key my-secret-key

# Import a shared vault
envault import team.vault --key my-secret-key
```

Add `.env` to your `.gitignore` and commit `.env.vault` safely to version control.

---

## How It Works

`envault` encrypts your `.env` files using AES-256 encryption. Each project gets its own vault file (`.env.vault`) that can be safely stored in version control. Team members decrypt the vault using a shared key, keeping secrets out of plaintext and out of your repository history.

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## License

[MIT](LICENSE)