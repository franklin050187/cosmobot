# cosmobot

A Discord bot for managing and searching the Cosmoship library. This bot allows users to search, upload, and manage ship designs through an intuitive Discord interface.

## Features

- 🔍 Advanced ship search with multiple filters:
  - Weapon tags (cannons, missiles, lasers, etc.)
  - User tags (thrust types, defense types, playstyles)
  - Utility tags (factories, reactors, shields, etc.)
  - Price range and crew size filters
  - Sorting by popularity, favorites, or newest
- 🚀 Ship upload functionality
- 📊 Detailed ship information display
- 🔗 Direct links to view and edit ships

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your environment variables
4. Run the bot:
   ```bash
   python bot.py
   ```

## Environment Variables

Create a `.env` file with the following variables:
- `DISCORD_API`: Your Discord bot token
- `URL_API`: API endpoint URL
- `URL_FRONT`: Frontend URL
- `TOKEN_SECRET`: Secret token for authentication (ask me to be added, used only for upload)

## Commands

- `/search`: Search for ships with advanced filtering options
- `/upload`: Upload a new ship design

## API Endpoints
- `URL_API`: need API in version 2, use https://cosmoship-api.hport.dev (non cached) or https://cosmoship-api-cdn.hport.dev (cached 4h TTL) (faster)
- `URL_FRONT`: use either new front https://cosmoship.hport.dev (non cached) | https://cosmoship-cdn.hport.dev (cached 4h TTL) or vercel host https://cosmo-lilac.vercel.app (slow but always up)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
