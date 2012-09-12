import sys, os, cssmin, optparse, urllib, json, re
from termcolor import colored
from datetime import date
from dateutil import parser

# initial options
base_dir            =   os.path.join(os.getcwd(), 'css')
tags                =   json.load(urllib.urlopen('https://api.github.com/repos/dryan/css-smart-grid/tags'))
current_version     =   tags[0]["name"]
latest_update       =   parser.parse(json.load(urllib.urlopen(tags[0]["commit"]["url"]))["commit"]["committer"]["date"])
gutter_width        =   20
columns             =   12
ie_fallback_class   =   "oldie"
ie_fallback_width   =   960
breakpoints =   [
    768,
    960,
    1200,
    1920,
]
breakpoint_suffixes =   [
    None,
    None,
    'large',
    'hd',
]
container_class                 =   'container'
column_class                    =   'columns'
minimum_container_with_columns  =   768

parser  =   optparse.OptionParser()
parser.add_option('--version', '-v', default = False, help = "The version to tag the files with. Defaults to the current latest tag from Github. Pass +1 to increment by 1 minor version.")
parser.add_option('--stdout', '-o', dest = "stdout", action="store_true", default = False, help = "Print to stdout.")
parser.add_option('--gutter-width', '-g', default = gutter_width, help = "The width of the gutters between each column.")
parser.add_option('--columns', '-c', default = columns, help = "The number of columns to create")
parser.add_option('--ie-fallback-class', default = ie_fallback_class, help = "The class name to use for IE fallback support. Defaults to 'oldie'.")
parser.add_option('--ie-fallback-width', default = ie_fallback_width, help = "The breakpoint to use for IE fallback support. Must be one of 320, 480, 768, 960, 1200 or 1920. Defaults to 960. A value under %d results in a single column layout." % minimum_container_with_columns)
parser.add_option('--debug', dest = "debug", action = "store_true", default = False, help = "Print debugging messages to stdout.")
opts, args   =   parser.parse_args()

if not opts.version and len(args):
    opts.version    =   args[0]

if opts.version and opts.version == '+1':
    cv              =   current_version.split('.')
    minor_number    =   int(cv.pop()) + 1
    cv.append(u'%d' % minor_number)
    current_version =   ".".join(cv)
    opts.version    =   current_version
    
if not opts.version:
    opts.version    =   current_version
else:
    latest_update   =   date.today()
        
if not re.search(r"^[\d]+\.[\d]+\.[\d]+$", opts.version):
    print colored("Version number %s is not in the format X.X.X" % opts.version, "red")
    sys.exit(os.EX_DATAERR)

if not type(opts.columns) == type(2):
    opts.columns    =   int(opts.columns)
    
if opts.columns % 2:
    print colored("Odd numbers of columns are not supported.", "red")
    sys.exit(os.EX_DATAERR)
    
if opts.columns > 48:
    print colored("%d is more columns than we support." % opts.columns, "red")
    sys.exit(os.EX_DATAERR)
    
if not type(opts.ie_fallback_width) == type(2):
    opts.ie_fallback_width  =   int(opts.ie_fallback_width)
    
if not opts.ie_fallback_width in breakpoints:
    print colored("%s is not a supported IE fallback width. Try one of %s." % (str(opts.ie_fallback_width), ", ".join("%s" % bp for bp in breakpoints)), "red")
    sys.exit(os.EX_DATAERR)
    
if not type(opts.gutter_width) == type(2):
    opts.gutter_width   =   int(opts.gutter_width)
    
if opts.debug:
    print "Options"
    for opt in dir(opts):
        if not opt.find('_') == 0 and not opt.find('read') > -1 and not opt.find('ensure') > -1:
            print "  %s: %s" % (opt, str(getattr(opts, opt)))
    print ""
    print "Arguments"
    for i in range(0, len(args)):
        print "  %d: %s" % (i, str(args[i]))
    print ""
    
print colored("Preparing to create version %s\n" % opts.version, "green")

custom_build    =   False
if ( not opts.columns == columns ) or ( not opts.gutter_width == gutter_width ) or ( not opts.ie_fallback_class == ie_fallback_class ) or ( not opts.ie_fallback_width == ie_fallback_width ):
    custom_build =   True

head_matter =   [
    '@charset "utf-8";',
    '',
    '/*',
    ' * smart-grid.css',
    ' * Created by Daniel Ryan on 2011-10-09',
    ' * Copyright 2011 Daniel Ryan. All rights reserved.',
    ' * Code developed under a BSD License: https://raw.github.com/dryan/css-smart-grid/master/LICENSE.txt',
    ' * Version: %s' % opts.version,
    ' * Latest update: %s' % latest_update.strftime('%Y-%m-%d'),
    ' */',
    '',
]

if custom_build:
    head_matter +=  [
        '/*',
        ' * Custom Build',
        ' * Columns: %d' % opts.columns,
        ' * Gutter Width: %d' % opts.gutter_width,
        ' * IE Fallback Class: %s' % opts.ie_fallback_class,
        ' * IE Fallback Width: %s' % opts.ie_fallback_width,
        ' */',
        '',
    ]
    
head_matter +=  [
    '/*',
    ' * Breakpoints:',
    ' * Tablet              -   768px',
    ' * Desktop             -   960px',
    ' * Widescreen          -   1200px',
    ' * Widescreen HD       -   1920px',
    ' */',
    '',
]
base_output =   [
    '/*',
    ' * Base container class',
    ' */',
    '.container {',
    '    padding: 0 %dpx;' % (opts.gutter_width / 2),
    '    margin: 0 auto;',
    '    clear: both;',
    '}',
    '',
    '/*',
    ' * contain rows of columns',
    ' */',
    '.row {',
    '    zoom: 1;',
    '    overflow: hidden;',
    '}',
    '',
]

output      =   []

def get_number_word(num):
    units   =   [
        'zero',
        'one',
        'two',
        'three',
        'four',
        'five',
        'six',
        'seven',
        'eight',
        'nine',
        'ten',
        'eleven',
        'twelve',
        'thirteen',
        'fourteen',
        'fifteen',
        'sixteen',
        'seventeen',
        'nineteen',
    ]
    
    tens    =   [
        '',
        '',
        'twenty',
        'thirty',
        'fourty',
    ]
    
    if num < len(units):
        return units[num]
    output  =   []
    pieces  =   ('%f' % (num / 10.0)).split('.')
    output.append(tens[int(pieces[0])])
    try:
        output.append(units[int(pieces[1].strip('0'))])
    except ValueError:
        # the second piece was all zeroes
        pass
    return "".join(output)
    

for i in range(0, len(breakpoints)):
    breakpoint          =   breakpoints[i]
    is_base             =   (breakpoint == breakpoints[0])
    container_width     =   breakpoint - opts.gutter_width
    column_width        =   (container_width - ((opts.columns - 1) * opts.gutter_width)) / opts.columns
    breakpoint_output   =   []
    ie_output           =   []
    breakpoint_suffix   =   '.' + breakpoint_suffixes[i] if breakpoint_suffixes[i] else ''
    
    # see if this breakpoint should also cover additional prefixes
    if breakpoint_suffixes[i]:
        for x in range(i, len(breakpoint_suffixes)):
            if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                breakpoint_output.append('\t.%s.%s,' % (container_class, breakpoint_suffixes[x]))

    # add the container width for this breakpoint
    breakpoint_output.append('\t.%s%s {' % (container_class, breakpoint_suffix))
    breakpoint_output.append('\t\twidth: %dpx;' % container_width)
    breakpoint_output.append('\t}')
    
    # work through the columns
    if breakpoint >= minimum_container_with_columns:
        fourths =   0
        thirds  =   0
        for col in range(1, opts.columns + 1):
            column_suffix   =   '.' + get_number_word(col) if col > 1 else ''
            col_width       =   col * column_width
            if col > 1:
                col_width   +=  (opts.gutter_width * (col - 1))
            # handle the special case names
            if opts.columns / 2.0 == float(col):
                if breakpoint_suffixes[i]:
                    for x in range(i, len(breakpoint_suffixes)):
                        if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                            breakpoint_output.append('\t.%s.%s .%s.one-half,' % (container_class, breakpoint_suffixes[x], column_class))
                breakpoint_output.append('\t.%s%s .%s.one-half,' % (container_class, breakpoint_suffix, column_class))
            if opts.columns / 4.0 == float(col):
                if breakpoint_suffixes[i]:
                    for x in range(i, len(breakpoint_suffixes)):
                        if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                            breakpoint_output.append('\t.%s.%s .%s.one-fourth,' % (container_class, breakpoint_suffixes[x], column_class))
                breakpoint_output.append('\t.%s%s .%s.one-fourth,' % (container_class, breakpoint_suffix, column_class))
                fourths +=  1
            if opts.columns / 3.0 == float(col):
                if breakpoint_suffixes[i]:
                    for x in range(i, len(breakpoint_suffixes)):
                        if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                            breakpoint_output.append('\t.%s.%s .%s.one-third,' % (container_class, breakpoint_suffixes[x], column_class))
                breakpoint_output.append('\t.%s%s .%s.one-third,' % (container_class, breakpoint_suffix, column_class))
                thirds  +=  1
            if (opts.columns / 4.0) * 3 == float(col):
                if breakpoint_suffixes[i]:
                    for x in range(i, len(breakpoint_suffixes)):
                        if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                            breakpoint_output.append('\t.%s.%s .%s.three-fourths,' % (container_class, breakpoint_suffixes[x], column_class))
                breakpoint_output.append('\t.%s%s .%s.three-fourths,' % (container_class, breakpoint_suffix, column_class))
                fourths +=  1
            if (opts.columns / 3.0) * 2 == float(col):
                if breakpoint_suffixes[i]:
                    for x in range(i, len(breakpoint_suffixes)):
                        if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                            breakpoint_output.append('\t.%s.%s .%s.two-thirds,' % (container_class, breakpoint_suffixes[x], column_class))
                breakpoint_output.append('\t.%s%s .%s.two-thirds,' % (container_class, breakpoint_suffix, column_class))
                thirds  +=  1
            if breakpoint_suffixes[i]:
                for x in range(i, len(breakpoint_suffixes)):
                    if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                        breakpoint_output.append('\t.%s.%s .%s%s,' % (container_class, breakpoint_suffixes[x], column_class, column_suffix))
            breakpoint_output.append('\t.%s%s .%s%s {' % (container_class, breakpoint_suffix, column_class, column_suffix))
            breakpoint_output.append('\t\twidth: %dpx;' % col_width)
            if col == 1 and breakpoint == minimum_container_with_columns:
                breakpoint_output.append('\t\tfloat: left;')
                breakpoint_output.append('\t\tmargin-left: %dpx;' % opts.gutter_width)
            breakpoint_output.append('\t}')
            if col < opts.columns:
                # do the offset
                # handle the special case names
                if opts.columns / 2.0 == float(col):
                    if breakpoint_suffixes[i]:
                        for x in range(i, len(breakpoint_suffixes)):
                            if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                                breakpoint_output.append('\t.%s.%s .offset-one-half,' % (container_class, breakpoint_suffixes[x]))
                    breakpoint_output.append('\t.%s%s .offset-one-half,' % (container_class, breakpoint_suffix))
                if opts.columns / 4.0 == float(col):
                    if breakpoint_suffixes[i]:
                        for x in range(i, len(breakpoint_suffixes)):
                            if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                                breakpoint_output.append('\t.%s.%s .offset-one-fourth,' % (container_class, breakpoint_suffixes[x]))
                    breakpoint_output.append('\t.%s%s .offset-one-fourth,' % (container_class, breakpoint_suffix))
                if opts.columns / 3.0 == float(col):
                    if breakpoint_suffixes[i]:
                        for x in range(i, len(breakpoint_suffixes)):
                            if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                                breakpoint_output.append('\t.%s.%s .offset-one-third,' % (container_class, breakpoint_suffixes[x]))
                    breakpoint_output.append('\t.%s%s .offset-one-third,' % (container_class, breakpoint_suffix))
                if (opts.columns / 4.0) * 3 == float(col):
                    if breakpoint_suffixes[i]:
                        for x in range(i, len(breakpoint_suffixes)):
                            if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                                breakpoint_output.append('\t.%s.%s .offset-three-fourths,' % (container_class, breakpoint_suffixes[x]))
                    breakpoint_output.append('\t.%s%s .offset-three-fourths,' % (container_class, breakpoint_suffix))
                if (opts.columns / 3.0) * 2 == float(col):
                    if breakpoint_suffixes[i]:
                        for x in range(i, len(breakpoint_suffixes)):
                            if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                                breakpoint_output.append('\t.%s.%s .offset-two-thirds,' % (container_class, breakpoint_suffixes[x]))
                    breakpoint_output.append('\t.%s%s .offset-two-thirds,' % (container_class, breakpoint_suffix))
                if breakpoint_suffixes[i]:
                    for x in range(i, len(breakpoint_suffixes)):
                        if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                            breakpoint_output.append('\t.%s.%s .offset-%s,' % (container_class, breakpoint_suffixes[x], get_number_word(col)))
                breakpoint_output.append('\t.%s%s .offset-%s {' % (container_class, breakpoint_suffix, get_number_word(col)))
                breakpoint_output.append('\t\tpadding-left: %dpx;' % (col_width + opts.gutter_width))
                breakpoint_output.append('\t}')
            if col == 1 and breakpoint == minimum_container_with_columns:
                if breakpoint_suffixes[i]:
                    for x in range(i, len(breakpoint_suffixes)):
                        if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                            breakpoint_output.append('\t.%s.%s .%s:first-child,' % (container_class, breakpoint_suffixes[x], column_class))
                            breakpoint_output.append('\t.%s.%s .%s.first,' % (container_class, breakpoint_suffixes[x], column_class))
                breakpoint_output.append('\t.%s%s .%s:first-child,' % (container_class, breakpoint_suffix, column_class))
                breakpoint_output.append('\t.%s%s .%s.first {' % (container_class, breakpoint_suffix, column_class))
                breakpoint_output.append('\t\tmargin-left: 0;')
                breakpoint_output.append('\t}')
        if fourths < 2:
            # we need to manually figure out the quarter column values
            one_fourth  =   (container_width - (opts.gutter_width * 3)) / 4
            if breakpoint_suffixes[i]:
                for x in range(i, len(breakpoint_suffixes)):
                    if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                        breakpoint_output.append('\t.%s.%s .%s.one-fourth,' % (container_class, breakpoint_suffixes[x], column_class))
            breakpoint_output.append('\t.%s%s .%s.one-fourth {' % (container_class, breakpoint_suffix, column_class))
            breakpoint_output.append('\t\twidth: %dpx;' % one_fourth)
            breakpoint_output.append('\t}')
            if breakpoint_suffixes[i]:
                for x in range(i, len(breakpoint_suffixes)):
                    if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                        breakpoint_output.append('\t.%s.%s .offset-one-fourth,' % (container_class, breakpoint_suffixes[x]))
            breakpoint_output.append('\t.%s%s .offset-one-fourth {' % (container_class, breakpoint_suffix))
            breakpoint_output.append('\t\tpadding-left: %dpx;' % one_fourth + opts.gutter_width)
            breakpoint_output.append('\t}')
            if breakpoint_suffixes[i]:
                for x in range(i, len(breakpoint_suffixes)):
                    if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                        breakpoint_output.append('\t.%s.%s .%s.three-fourths,' % (container_class, breakpoint_suffixes[x], column_class))
            breakpoint_output.append('\t.%s%s .%s.three-fourths {' % (container_class, breakpoint_suffix, column_class))
            breakpoint_output.append('\t\twidth: %dpx;' % ((one_fourth * 3) + (opts.gutter_width * 2)))
            breakpoint_output.append('\t}')
            if breakpoint_suffixes[i]:
                for x in range(i, len(breakpoint_suffixes)):
                    if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                        breakpoint_output.append('\t.%s.%s .offset-three-fourths,' % (container_class, breakpoint_suffixes[x]))
            breakpoint_output.append('\t.%s%s .offset-three-fourths {' % (container_class, breakpoint_suffix))
            breakpoint_output.append('\t\tpadding-left: %dpx;' % ((one_fourth * 3) + (opts.gutter_width * 3)))
            breakpoint_output.append('\t}')
        if thirds < 2:
            # we need to manually figure out the third column values
            one_third   =   (container_width - (opts.gutter_width * 2)) / 3
            if breakpoint_suffixes[i]:
                for x in range(i, len(breakpoint_suffixes)):
                    if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                        breakpoint_output.append('\t.%s.%s .%s.one-third,' % (container_class, breakpoint_suffixes[x], column_class))
            breakpoint_output.append('\t.%s%s .%s.one-third {' % (container_class, breakpoint_suffix, column_class))
            breakpoint_output.append('\t\twidth: %dpx;' % one_third)
            breakpoint_output.append('\t}')
            if breakpoint_suffixes[i]:
                for x in range(i, len(breakpoint_suffixes)):
                    if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                        breakpoint_output.append('\t.%s.%s .offset-one-third,' % (container_class, breakpoint_suffixes[x]))
            breakpoint_output.append('\t.%s%s .offset-one-third {' % (container_class, breakpoint_suffix))
            breakpoint_output.append('\t\tpadding-left: %dpx;' % (one_third + opts.gutter_width))
            breakpoint_output.append('\t}')
            if breakpoint_suffixes[i]:
                for x in range(i, len(breakpoint_suffixes)):
                    if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                        breakpoint_output.append('\t.%s.%s .offset-two-thirds,' % (container_class, breakpoint_suffixes[x]))
            breakpoint_output.append('\t.%s%s .offset-two-thirds {' % (container_class, breakpoint_suffix))
            breakpoint_output.append('\t\tpadding-left: %dpx;' % (one_third * 2) + (opts.gutter_width * 2))
            breakpoint_output.append('\t}')
            
        # do the fifths
        one_fifth   =   (container_width - (opts.gutter_width * 4)) / 5
        for fifth in range(1,6):
            if breakpoint_suffixes[i]:
                for x in range(i, len(breakpoint_suffixes)):
                    if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                        breakpoint_output.append('\t.%s.%s .%s.%s-fifth%s,' % (container_class, breakpoint_suffixes[x], column_class, get_number_word(fifth), 's' if fifth > 1 else ''))
            breakpoint_output.append('\t.%s%s .%s.%s-fifth%s {' % (container_class, breakpoint_suffix, column_class, get_number_word(fifth), 's' if fifth > 1 else ''))
            breakpoint_output.append('\t\twidth: %dpx;' % ((one_fifth * fifth) + (opts.gutter_width * (fifth - 1))))
            breakpoint_output.append('\t}')
            if breakpoint_suffixes[i]:
                for x in range(i, len(breakpoint_suffixes)):
                    if not breakpoint_suffixes[x] == breakpoint_suffix.strip('.'):
                        breakpoint_output.append('\t.%s.%s .offset-%s-fifth%s,' % (container_class, breakpoint_suffixes[x], get_number_word(fifth), 's' if fifth > 1 else ''))
            breakpoint_output.append('\t.%s%s .offset-%s-fifth%s {' % (container_class, breakpoint_suffix, get_number_word(fifth), 's' if fifth > 1 else ''))
            breakpoint_output.append('\t\tpadding-left: %dpx;' % ((one_fifth * fifth) + (opts.gutter_width * fifth)))
            breakpoint_output.append('\t}')
            
                
    if breakpoint == opts.ie_fallback_width:
        ie_output   =   [
            '',
            '/*',
            ' * IE Fallback: %dpx' % breakpoint,
            ' */',
        ]
        for line in breakpoint_output:
            ie_output.append(re.sub(r'^\t', '', line.replace('.%s' % container_class, '.%s .%s' % (opts.ie_fallback_class, container_class))))
        if breakpoint >= minimum_container_with_columns:
            ie_output.append('.%s .%s .%s {' % (opts.ie_fallback_class, (container_class + '.' + breakpoint_suffix if len(breakpoint_suffix) else container_class), column_class))
            ie_output.append('\tfloat: left;')
            ie_output.append('\tmargin-left: %dpx;' % opts.gutter_width)
            ie_output.append('}')
            ie_output.append('.%s .%s .%s:first-child,' % (opts.ie_fallback_class, (container_class + '.' + breakpoint_suffix if len(breakpoint_suffix) else container_class), column_class))
            ie_output.append('.%s .%s .%s.first {' % (opts.ie_fallback_class, (container_class + '.' + breakpoint_suffix if len(breakpoint_suffix) else container_class), column_class))
            ie_output.append('\tmargin-left: 0;')
            ie_output.append('}')
            
    # wrap these rules in a media query
    breakpoint_output.insert(0, '@media screen and (min-width:%dpx) {' % breakpoint)
    # insert the comments about this breakpoint
    breakpoint_output.insert(0, ' */')
    breakpoint_output.insert(0, ' * Breakpoint: %dpx' % breakpoint)
    breakpoint_output.insert(0, '/*')
    # close the media query
    breakpoint_output.append('}')

    # push this group onto the main output
    output  =   output + breakpoint_output
    if len(ie_output):
        output  =   ie_output + output

if opts.stdout:
    print "\n".join(head_matter)
    print "\n".join(base_output)
    print "\n".join(output)
else:
    filename    =   'smart-grid.css'
    if custom_build: # our default
        filename    =   'smart-grid-custom-%s.css' % datetime.now().strftime('%Y%m%d%H%M%S')
    filename_min    =   filename.replace('.css', '.min.css')
    f               =   open(os.path.join(base_dir, filename), 'w')
    f.write("\n".join(head_matter))
    f.write("\n".join(base_output))
    f.write("\n".join(output))
    f.flush()
    f.close()
    f               =   open(os.path.join(base_dir, filename_min), 'w')
    f.write("\n".join(head_matter))
    f.write(cssmin.cssmin("\n".join(base_output)))
    f.write(cssmin.cssmin("\n".join(output)))
    f.flush()
    f.close()
    
    print colored("%s and %s version %s have been saved." % (filename, filename_min, opts.version), "green")
    print ""
    sys.exit(os.EX_OK)