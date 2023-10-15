# VTTShift

A simple tool to shift time ranges in of WebVTT files.

## Installation

Sheesh, I don’t know.
I tried to follow the latest Python packaging guidelines,
but I don’t think I’ve gone through all the way with making a published executable package.
I use a venv with `pip install -e .`, then run the program with `python -m vttshift`;
[pipx](https://pypa.github.io/pipx/) might work for you?

## Usage

VTTShift reads a WebVTT subtitle file on standard input
and writes an adjusted version to standard output.
Adjustments are specified in the command line arguments,
as a timestamp followed by a positive or negative number of milliseconds:

```sh
python -m vttshift '15:00+2000' '17:00-3000' < in.vtt > out.vtt
```

A positive adjustment like `+2000` (two seconds) is added to timestamps,
effectively creating a “gap” in the subtitles;
this is useful if the subtitles are “ahead” of the video.
A negative adjustment like `-3000` (three seconds) is subtracted from timestamps,
effectively removing a “gap” in the subtitles;
this is useful if the subtitles “lag behind” the video.
(No subtitles are ever removed:
if there wasn’t a “gap” in the subtitles,
some subtitles might overlap afterwards.)
Each adjustment is independent and only takes effect until the next adjustment;
in the example above, two seconds are added to timestamps between 15:00 and 17:00,
whereas after 17:00 three seconds are subtracted from timestamps.

If you’re confident that this tool does the right thing,
or you can easily get the input subtitles back (e.g. from a backup),
you can use the `sponge` utility from [moreutils](https://joeyh.name/code/moreutils/)
to overwrite the input file instead of having a separate output file:

```sh
python -m vttshift '15:00+2000' '17:00-3000' < file.vtt | sponge file.vtt
```

(Don’t use `< file.vtt > file.vtt` with the same file name –
that just results in an empty file.)

## License

[Blue Oak Model License 1.0.0](https://blueoakcouncil.org/license/1.0.0).
