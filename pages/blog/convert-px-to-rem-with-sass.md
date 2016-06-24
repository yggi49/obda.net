title: Convert px to rem with Sass
published: 2016-06-24
tags: [web-development, sass]

The following [Sass][1] function converts pixels to [rem][2]:

    :::scss
    @function px-rem($size, $base: 16px) {
        @if (unitless($size)) {
            $size: $size * 1px;
        }
        @if (unitless($base)) {
            $base: $base * 1px;
        }
        @return 1rem * ($size / $base);
    }

The `$size` argument can be provided either with or without a `px` unit, for
example:

    :::scss
    font-size: px-rem(18px);   /* 1.125rem */
    line-height: px-rem(24);   /* 1.5rem */

You can provide a second argument to `px-rem()` if your base font size is not
16 pixels.

[1]: http://sass-lang.com/
[2]: https://snook.ca/archives/html_and_css/font-size-with-rem
