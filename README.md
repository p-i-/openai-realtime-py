# OpenAI Realtime API Python Edition

Python implementation of OpenAI's realtime API

Guide [here](https://platform.openai.com/docs/guides/realtime)

API Ref [here](https://platform.openai.com/docs/api-reference/realtime-client-events)

OpenAI have sample code ([openai-realtime-console](https://github.com/openai/openai-realtime-console)) but it is JavaScript-based.

So here's a start at a Python implementation.


# Getting it running

- Create a Virtual Environment if you want to: `python -m venv .venv ;  ./.venv/bin/activate`

- `pip install -r requirements.txt`

- Create a `.env` file like `.env.template` filling in your OpenAI API key

- Run it

You can run the legacy files: `python legacy/realtime-simple.py` or `python legacy/realtime-classes.py` which work while being minimal (especially the first one). Probably good for getting a feeling of how it works.

Alternatively `cd src; python main.py` -- this is the codebase I'll be building off moving forwards.


# Notes:

## legacy/
- `legacy/realtime-simple.py` is "Least number of lines that gets the job done"
- `legacy/realtime-classes.py` is arguably tidier

Both work! The AI talks to you, and you can talk back.

I have to mute the mic while the AI is speaking, else it gets back its own audio and gets very (entertainingly) confused. "Hello, I'm a helpful assistant!" "Gosh, so am I!" "What a coincidence!" "I know, right?!", etc.

## src/ (current/future)
I've abstracted websocket-stuff and audioIO-stuff into Socket.py and AudioIO.py, which leaves Realtime.py free to make more sense.

I did take a run at doing this async with Trio, but at this point it just gets in the way. Maybe I'll return to an async model. I'm not sold on it, much as I love Trio; exception-handling and teardown are a pain.


# Vision

It would be nice to clean this up to act as a fully-featured Python API for this service.


# Do involve!

Contributions are invited, in which case you are welcome to contact the author (You'll find a link to the sap.ient.ai Discord on https://github.com/sap-ient-ai upon which I exist as `_p_i_`).


# Thanks

Thanks to https://www.naptha.ai/ for providing vital funding that allows me to Do My Own Thing.
