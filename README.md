# APK_patcher

## What is it? 

APK_patcher is a tool that lets you:

- Extract APK contents into a folder.

- Decompile classes.dex into smali.

- Patch the decompiled smali with a patch.txt (you can see the format in patch_example.txt), which must be present as "patch.txt" in the same folder you decompiled the APK.
- Rebuild and sign your apk (providing your custom signing script).

## Installation

- You will need to have java jdk21 installed on your system.
- Just put your patcher.py in your working directory, then run it as showed in usage.

## Usage

- Usage:

```bash
    ./patcher.py <command> <option> [file]

    COMMANDS:
        
        baksmali
        patch
        smali
        build <signing_script_path>
        sign  <signing_script_path>

    OPTIONS:
        -r  rebuild the patch folder
        -c  smali only the following class
        -t  max number of threads wile compiling/decompiling

```

- patch.txt example:

```java
// Java syntax highlighting is really good for this file format.

// Replace the 1st line with 'const/16 v0, 0x0' in the file 'example.smali' 
// extracted from the class 'classes.dex' 

[classes/example/example.smali:1:w]
{    const/16 v0, 0x0}

// Appends after the 10th line 'const/16 v0, 0x0' for 5 rows in the file 'example2.smali' 
// extracted from the class 'classes2.dex'

[classes2/example2/example2.smali:10:a]
{    const/16 v0, 0x0}
{    const/16 v0, 0x0}
{    const/16 v0, 0x0}
{    const/16 v0, 0x0}
{    const/16 v0, 0x0}

// Removes five lines starting from the 206th line in the file 'example3.smali' 
// extracted from the class 'classes3.dex'

[classes3/example3/example3.smali:206:w]
{}
{}
{}
{}
{}

```
## License

[MIT](https://choosealicense.com/licenses/mit/)