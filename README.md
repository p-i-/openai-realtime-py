# OpenAI Realtime API Python Edition

Python implementation of OpenAI's realtime API

OpenAI have a Node.js + JavaScript wrapper [here](https://github.com/openai/openai-realtime-api-beta), as well as a [openai-realtime-console](https://github.com/openai/openai-realtime-console) demo-project, but as yet nothing in Python, so here's a start at fixing that!

### A couple of useful links:
- [Guide](https://platform.openai.com/docs/guides/realtime)
- [API Reference](https://platform.openai.com/docs/api-reference/realtime-client-events)


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

## Additional note (7 Oct 2024)
After some testing, it's clear that legacy/realtime-simple.py functions crisply, and there is some responsiveness issue with src/.

This could be a locking issue, with audio arriving from the websocket into an input buffer, which is, on a worker thread, drained to the speakers. It could be with mic-data, which is buffered in a worker thread and drained to the websocket. It could be both, and/or something else.

Python is not an ideal language for realtime audio processing, and likely this was factored into account by the OpenAI team's decision to initially publish only a Node.js implementation.

# Vision

It would be nice to clean this up to act as a fully-featured Python API for this service.


# TODO

- Firstly the code needs picking through, to ensure a clean / robust skeleton.

- EDIT: Actually the architecture in src/ needs to be revised, to account for the above Additional Note.

- Need some thought on what such a lib should expose & how to expose it (e.g. callbacks).

- Fleshing out API support (it's quite a big API).

- Tool-Use / Function-Calling.

- User-interruption-support via feedback cancellation (currently I'm having to mute the mic while openAI audio is playing out of the speakers, which means I can't interrupt it). There's WebRTC AEC (Adaptive Echo Cancellation), but I can't find any off-the-shelf pip library that doesn't require fiddling (building deps). Maybe `pip install adaptfilt` is a good solution. This looks doable.


# Do involve!

Contributions are invited, in which case you are welcome to contact the author (You'll find a link to the sap.ient.ai Discord on https://github.com/sap-ient-ai upon which I exist as `_p_i_`).


# Thanks

Thanks to https://www.naptha.ai/ for providing vital funding that allows me to Do My Own Thing.
