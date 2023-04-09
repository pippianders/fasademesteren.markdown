import argparse
import os
import logging
import re
import shutil

def note_files(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".md"):
                yield (
                    os.path.join(root, file),                                       # get md file
                    [os.path.join(root, d) for d in dirs if d.endswith('.assets')]  # get corresponfing assets directories
                )

def parse_header(mdtext):
    yaml_beg = mdtext.find('---') # should be 0
    yaml_end = mdtext.find('---', yaml_beg + 1)
    title = "# title"
    match = re.search(r'# (.*)', mdtext)

    if match is None:
        raise Exception("Can't find the title!")
    else:
        title = match.group(1)

    return mdtext[:yaml_end] + f'title: "{title}"\n' + mdtext[yaml_end:]

def replace_directories(mdtext, dirs, dst):
    target = "/img/" + dirs
    return mdtext.replace(dirs, target).replace("./" + dirs, target)

def convert(in_dir, out_notes, out_assets):
    for note, assets in note_files(in_dir):
        mdtext = None
        with open(note, 'r') as f:
            mdtext = f.read()
        
        try:
            # parse header and assets
            mdtext = parse_header(mdtext)
            asset = None

            if len(assets) > 0:
                asset = assets[0]
                dir_basename = os.path.basename(asset)
                dst_assets = os.path.join(out_assets, dir_basename)
                mdtext = replace_directories(mdtext, dir_basename, dst_assets)
            
            # save
            note_original_dir = os.path.dirname(note)
            note_relative_dir = note_original_dir.replace(in_dir, "")[1:] # remove leading slash
            note_output_dir = os.path.join(out_notes, note_relative_dir)
            if not os.path.exists(note_output_dir):
                logging.info(f"Destination directory didn't exist, creating it: {note_output_dir}")
                os.makedirs(note_output_dir)
            
            with open(os.path.join(note_output_dir, os.path.basename(note)), 'w') as f:
                f.write(mdtext)

            if asset != None:
                if os.path.exists(dst_assets):
                    shutil.rmtree(dst_assets)
                shutil.copytree(asset, dst_assets)
        
        except Exception as e:
            logging.error("Exception: ", e)
            return

def main():
    parser = argparse.ArgumentParser(description="Script for converting md notes into hugo-compatibile pages")
    
    parser.add_argument('in_dir', type=str,help="Path to root notes directory")
    parser.add_argument('out_notes', type=str, help="Output directory for md notes")
    parser.add_argument('out_assets', type=str, help="Output directory for assets (i.e local images)")
    parser.add_argument('-v', dest='verbose', action="store_true", help="Enable debug logging", default=False)

    args = parser.parse_args()
    
    # change loglever
    loglevel = logging.ERROR
    if args.verbose:
        loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel)

    # check existance of directories
    if not os.path.exists(args.in_dir):
        logging.error("Can't find input directory!")
        return

    for d in [args.out_notes, args.out_assets]:
        if not os.path.exists(d):
            logging.info(f"Create not existed directory: {d}")
            os.makedirs(d)
    
    # run code
    convert(args.in_dir, args.out_notes, args.out_assets)

if __name__ == "__main__":
    main()