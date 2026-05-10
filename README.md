# Twitch Yap Stats

Silly python script to get some stats from twitch chat, such as: which user yaps the most, average message length, most used words

## How to Run

### Registering a Twitch Application

- Head over to <https://dev.twitch.tv/console>
- Log in to your twitch account
- Click on "Register Your Application"
- Give it a nice name
- For this program, set OAuth Redirect URL to: <http://localhost:17563>
- Click Create

### Getting App Keys

- Head back to <https://dev.twitch.tv/console>
- Click on "Manage" on the application you just created
- The Client ID should already be at the bottom
- Click New Secret to generate a Secret ID
- Keep these safe and ready to input later on, don't leak them

### Running the Program

#### NOTE HAS ONLY BEEN TESTED ON PYTHON 3.12

- Clone the repository
- Download python 3.12 or higher if you don't have it already
- Create a virtual environment and activate it (optional but recommended)
   - `python -m venv venv`
   - `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Unix)
- Install uv using `pip install uv -c constraints.txt`
- Install dependencies using `uv sync`
- Run `yap_server` (This will run in the background and needs to be done only once)
  - You will be prompted to input your Client ID and Secret if not present
- Run `yap_stats` and follow the prompts

## Todo

- Check if stream is live
  - Update flow, dynamically set `DATE` variable
- Allow it to work for multiple streams
- ~~Nicer user access to customisability~~
- ~~Exclude links~~, **maybe** emojis/punctuation
- *Possibly* switch to App authentication (possibly eliminate use of `server.py`)
- Allow to simultaneously run on multiple channels

## Credits

### <https://pytwitchapi.dev/en/stable>

### shdewz for basically coming up with this sort of statistic, [example (under extra statistics in bottom right)](https://docs.google.com/spreadsheets/d/1OGcjc_Kt5rV493JeFSB-dzPgXdUnpW_FuXEjI8IrE2s/edit?rm=minimal&gid=1481733015#gid=1481733015)
