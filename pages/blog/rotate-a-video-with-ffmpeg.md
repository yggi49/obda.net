title: 'Rotate a Video with ffmpeg'
published: 2014-08-26
tags: [linux, cheat-sheet, ffmpeg]

{% include 'cheat-sheet.md' %}

The `transpose` video filter of ffmpeg allows rotating a video by 90 degrees:

    :::bash
    ffmpeg -i in.mp4 -vf 'transpose=1' out.mp4

Specify a value from 0–3 as `transpose`’s argument:

Value | Description
- | -
`0` | Rotate by 90 degrees counterclockwise and flip vertically (default)
`1` | Rotate by 90 degrees clockwise
`2` | Rotate by 90 degrees counterclockwise
`3` | Rotate by 90 degrees clockwise and flip vertically
