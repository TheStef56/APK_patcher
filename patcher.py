#!/usr/bin/python3

from concurrent.futures import ThreadPoolExecutor, as_completed
import sys, os, shutil, subprocess

APK           = ""
PATCH_FILE    = "patch.txt"
MAX_THREADS   = 4
BASE_PATH     = os.path.sep.join(os.path.abspath(__file__).split(os.path.sep)[:-1])
BAKSMALI_PATH = os.path.join(BASE_PATH, "jar", "baksmali-3.0.9-fat-release.jar")
SMALI_PATH    = os.path.join(BASE_PATH, "jar", "smali-3.0.9-fat-release.jar")
ZIP_PATH      = os.path.join(BASE_PATH, "jar", "zip.jar")
UNZIP_PATH    = os.path.join(BASE_PATH, "jar", "unzip.jar")
PREFIX        = "\\\\?\\" if os.name == 'nt' else ""

def usage():
     print(
"""Usage:

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
"""
    )

def run_command(command):
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return (command, result.returncode, result.stdout.strip(), result.stderr.strip())
    except Exception as e:
        return (command, -1, "", str(e))

def run_cmd_threaded(commands):
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(run_command, cmd) for cmd in commands]

        for future in as_completed(futures):
            command, returncode, stdout, stderr = future.result()
            print(f"CMD: {command}, ret: {returncode}, {stdout} {stderr} ")

def check_patch_dir():
    exists = os.path.exists("patch")
    if "-r" in sys.argv or not exists:
        print("Generating Patch folder ...")
        if exists: shutil.rmtree(PREFIX + os.path.abspath("patch"))

        os.mkdir("patch")
        os.system(f"java -jar {UNZIP_PATH} {APK} patch")
        os.chdir("patch")
        os.mkdir("smali_all")
        os.mkdir("dex_old")
        os.chdir("..")

def baksmali():
    os.chdir("patch")
    cmds = []
    for file in os.listdir("."):
        if file.endswith(".dex"):
            cmds.append(f"java -jar {BAKSMALI_PATH} d {file} -o ./smali_all/{file[:-4]}")
    run_cmd_threaded(cmds)
    os.chdir("..")

def patch():
    with open(PATCH_FILE, "r") as patchfile:
        pflines = patchfile.readlines()
        path = ""
        linen = 0
        mode = ""
        for line in pflines:
            if line.startswith("["):
                lspl = line.split(":")
                path = lspl[0][1:]   
                linen = int(lspl[1])
                mode = lspl[2][:-2]
                patchlc = 0
                
                print(f"Patching {path}")

                file = path.split("/")[-1]
                basep = "/".join(path.split("/")[:-1])
                
                for caseinsfile in os.listdir(f"./patch/smali_all/{basep}"):
                    if file.split(".")[0] == caseinsfile.split(".")[0]:
                        fp = os.path.join("./patch/smali_all", basep, caseinsfile)
                        with open(fp, "r") as topatch:
                            old = topatch.readlines()
                        
                        if (linen - 1) > len(old):
                            print("ERROR: patch line higher than max .smali file lines")
                            exit(1)

            elif line.startswith("{"):
                res = line.replace("\n", "")[1:-1]
                content = f"{res}\n"
        
                with open(fp, "w") as patched:
                    if mode == "w":
                        old[linen + patchlc - 1] = content
                    elif mode == "a":
                        if old[linen + patchlc - 1] != content:
                            old.insert(linen + patchlc - 1, content)
                    patched.writelines(old)
                    patchlc += 1



def smali():
    cmds = []
    os.chdir("patch")
    for file in os.listdir("."):
        if file.endswith(".dex"):
            if "-c" in sys.argv and file.split(".")[0] != sys.argv[sys.argv.index("-c") + 1]:
                continue
            if not os.path.exists(f"dex_old/{file}"):
                shutil.move(file, f"dex_old/{file}")
    for classe in os.listdir("smali_all"):
        if "-c" in sys.argv and classe != sys.argv[sys.argv.index("-c") + 1]:
            continue
        cmds.append(f"java -jar {SMALI_PATH} a smali_all/{classe} -o {classe}.dex")
    run_cmd_threaded(cmds)
    os.chdir("..")

def build(sign_script):
    print("Generating patched APK")
    os.chdir("patch")
    try:
        os.remove("../patched_aligned.apk")
    except:
        pass
    os.system(f"java -jar {ZIP_PATH}")
    os.chdir("..")
    os.system("zipalign -v -p 4 patched.apk patched_aligned.apk >nul")
    print("Patched APK generated")
    sign(sign_script)

def sign(sign_script):
    print("Signing APK")
    if not os.system(sign_script):
        print("APK signed")
    else:
        print("Error signing APK")

def patchall(sign_script):
    baksmali()
    patch()
    smali()
    build(sign_script)

def main():
    global APK, MAX_THREADS
    if len(sys.argv) < 2:
        usage()
        return 1
    APK = sys.argv[-1]
    check_patch_dir()
    
    if '-t' in sys.argv:
        MAX_THREADS = int(sys.argv.index('-t') + 1)

    if "baksmali" in sys.argv:
        baksmali()
    if "patch" in sys.argv:
        patch()
    if "smali" in sys.argv:
        smali()
    if "build" in sys.argv:
        if len(sys.argv) < 3:
            usage()
            return 1
        build(sys.argv[2])
    if sys.argv[1] == "patchall":
        if len(sys.argv) < 4:
            usage()
            return 1
        patchall(sys.argv[2])
        return 0
    elif sys.argv[1] == "sign":
        sign(sys.argv[2])
        return 0

if __name__ == "__main__":
    main()