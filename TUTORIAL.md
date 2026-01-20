# C++ Build & Package Management Tutorial

A beginner-friendly guide to understanding CMake, Conan, and JFrog in the context of cross-platform C++ development.

---

## Table of Contents
1. [The Problem We're Solving](#the-problem-were-solving)
2. [CMake: Building C++ Projects](#cmake-building-c-projects)
3. [Conan: Managing Dependencies](#conan-managing-dependencies)
4. [JFrog Artifactory: Hosting Packages](#jfrog-artifactory-hosting-packages)
5. [How They Work Together](#how-they-work-together)
6. [Real World Example](#real-world-example)

---

## The Problem We're Solving

### Scenario: Building a C++ Library

Imagine you're building a C++ math library (`mylib`) that:
- Needs to work on **Linux, macOS, and Windows**
- Uses **GoogleTest** for unit testing
- Should be **easy to install** for other developers
- Needs **version control** for releases

**Challenges:**
1. ❌ Different compilers (gcc, clang, MSVC)
2. ❌ Different build systems per platform
3. ❌ Manually downloading/building dependencies (GoogleTest)
4. ❌ Sharing your library with others requires complex instructions
5. ❌ No central place to store different versions

**Solution:** CMake + Conan + JFrog

---

## CMake: Building C++ Projects

### What is CMake?

**CMake** = **C**ross-platform **Make**

Think of CMake as a "universal translator" for C++ build systems.

```
Your Code (C++)
     ↓
  CMake (translates)
     ↓
┌────────┬────────┬────────┐
│ Linux  │ macOS  │Windows │
│ Make   │ Xcode  │ MSVC   │
└────────┴────────┴────────┘
```

### Why Not Just Use Make/Visual Studio?

**Without CMake:**
```bash
# Linux developer
$ g++ src/*.cpp -o mylib

# Windows developer (different commands!)
> cl.exe src\*.cpp /Fe:mylib.exe

# macOS developer (different again!)
$ clang++ src/*.cpp -o mylib
```

**With CMake:**
```bash
# ALL platforms use the same commands:
$ cmake -B build
$ cmake --build build
$ ctest --test-dir build
```

### CMake Example

**CMakeLists.txt** (configuration file):
```cmake
cmake_minimum_required(VERSION 3.15)
project(mylib VERSION 1.0.0)

# Add your library
add_library(mylib src/sum.cpp)

# Specify include directories
target_include_directories(mylib PUBLIC include)

# Add tests
enable_testing()
add_subdirectory(tests)
```

**What CMake does:**
1. Reads `CMakeLists.txt`
2. Detects your compiler (gcc/clang/MSVC)
3. Generates native build files (Makefile/Xcode/Visual Studio)
4. You run one command to build on any platform

### Key Concepts

**Target** = Something you're building (library, executable, test)
```cmake
add_library(mylib ...)       # Creates a library target
add_executable(app ...)      # Creates an executable target
```

**Include Directories** = Where header files (.h) are located
```cmake
target_include_directories(mylib PUBLIC include)
```

**Linking** = Connecting your code to dependencies
```cmake
target_link_libraries(mylib PUBLIC other_library)
```

---

## Conan: Managing Dependencies

### What is Conan?

**Conan** = Package manager for C++ (like npm for Node.js, pip for Python)

**The Dependency Problem:**

Your `mylib` needs GoogleTest for unit testing:

**Without Conan:**
```bash
# Manual download
$ wget https://github.com/google/googletest/releases/...
$ tar -xzf googletest.tar.gz
$ cd googletest
$ mkdir build && cd build
$ cmake ..
$ make
$ make install  # Hope it goes to the right place!

# Now update your CMake to find it...
# Different paths on Linux/macOS/Windows 😱
```

**With Conan:**
```python
# conanfile.py
requires = "gtest/1.14.0"  # That's it!
```

```bash
$ conan install .  # Downloads, builds, installs automatically
```

### How Conan Works

```
┌─────────────────┐
│ Your Project    │
│ conanfile.py    │
│ requires gtest  │
└────────┬────────┘
         │
         ↓ conan install
┌────────────────────────┐
│ Conan Center (Remote)  │
│ gtest/1.14.0           │
│ zlib/1.3.1             │
│ boost/1.80.0           │
└────────┬───────────────┘
         │
         ↓ Downloads & Builds
┌────────────────────────┐
│ Local Cache            │
│ ~/.conan2/             │
│   gtest/1.14.0/        │
│     lib/               │
│     include/           │
└────────┬───────────────┘
         │
         ↓ Generates
┌────────────────────────┐
│ CMake Files            │
│ build/generators/      │
│   FindGTest.cmake      │
│   conan_toolchain.cmake│
└────────────────────────┘
```

### Conan Package Recipe (conanfile.py)

```python
from conan import ConanFile
from conan.tools.cmake import CMake

class MyLibConan(ConanFile):
    name = "mylib"
    version = "1.0.0"
    
    # What you need to build
    settings = "os", "arch", "compiler", "build_type"
    
    # Your dependencies
    requires = "gtest/1.14.0"
    
    # CMake integration
    generators = "CMakeDeps", "CMakeToolchain"
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
    
    def package(self):
        cmake = CMake(self)
        cmake.install()
```

### Conan Workflow

```bash
# 1. Install dependencies
$ conan install . --build=missing
# Downloads gtest, generates CMake files

# 2. Build your project
$ cmake --preset conan-release
$ cmake --build --preset conan-release

# 3. Create package
$ conan create . --version=1.0.0
# Builds and packages mylib

# 4. Upload to remote
$ conan upload mylib/1.0.0 --remote=my-repo
# Shares with team
```

### Why Conan?

| Without Conan | With Conan |
|---------------|------------|
| Manual dependency downloads | `conan install .` |
| Complex build instructions | Automated |
| Version conflicts | Explicit version pinning |
| Platform-specific paths | Conan handles it |
| Hard to share libraries | `conan upload` |

---

## JFrog Artifactory: Hosting Packages

### What is JFrog?

**JFrog Artifactory** = A warehouse for your compiled packages

Think of it as **GitHub for binaries** instead of source code.

### The Sharing Problem

You've built `mylib` and want your team to use it:

**Without JFrog:**
```bash
# You: Build on your machine
$ cmake --build build

# Email the .a/.lib file to coworker?
# Put on shared drive?
# How do they know which version?
# What if they use different OS/compiler?
```

**With JFrog:**
```bash
# You: Upload once
$ conan upload mylib/1.0.0 --remote=jfrog-repo

# Coworker: Download and use
$ conan install --requires=mylib/1.0.0
# Gets correct version for their OS/compiler automatically
```

### JFrog Repositories

In this project, we use **3 remotes**:

```
┌───────────────────────────────────┐
│         Conan Remotes             │
├───────────────────────────────────┤
│                                   │
│  📦 conancenter (Public)          │
│     ├─ gtest/1.14.0               │
│     ├─ boost/1.80.0               │
│     └─ zlib/1.3.1                 │
│                                   │
│  🧪 conan-rc (Private - Testing)  │
│     ├─ mylib/3.0.0-dev-7fcce98    │ ← Release Candidate
│     └─ mylib/2.3.0-dev-abc1234    │
│                                   │
│  ✅ conan-stable (Private - Prod) │
│     ├─ mylib/3.0.0                │ ← Official Release
│     ├─ mylib/2.2.1                │
│     └─ mylib/2.2.0                │
│                                   │
└───────────────────────────────────┘
```

**Remote Types:**

1. **conancenter** (public)
   - Maintained by Conan team
   - Open-source packages (gtest, boost, etc.)
   - Free to use
   - Read-only for most users

2. **conan-rc** (your private JFrog)
   - Release Candidates (testing versions)
   - Format: `mylib/3.0.0-dev-7fcce98`
   - Contains git SHA for traceability
   - Only your team can access

3. **conan-stable** (your private JFrog)
   - Production releases
   - Format: `mylib/3.0.0`
   - Clean versions without -dev suffix
   - Approved for customer use

### Why Separate RC and Stable?

```
Developer workflow:

1. PR Created → Build → Test
        ↓
2. Add "publish" label
        ↓
3. Build RC: mylib/3.0.0-dev-7fcce98
        ↓ Upload to conan-rc
4. Integration tests (consumer-verify)
        ↓
5. Tests pass → Merge PR
        ↓
6. Build Release: mylib/3.0.0 (clean)
        ↓ Upload to conan-stable
7. Customers can now use it!
```

**Benefits:**
- ✅ Test before releasing (RC in conan-rc)
- ✅ Production versions are clean (no -dev suffix)
- ✅ Easy rollback (keep old versions in conan-stable)
- ✅ Traceability (RC versions have git SHA)

### JFrog Configuration

**Remotes setup:**
```bash
# Add your JFrog Artifactory remotes
$ conan remote add conan-rc https://your-company.jfrog.io/artifactory/api/conan/rc-repo
$ conan remote add conan-stable https://your-company.jfrog.io/artifactory/api/conan/stable-repo

# Add public remote
$ conan remote add conancenter https://center.conan.io

# Authenticate
$ conan remote login conan-rc myusername -p mytoken
```

**In CI/CD (GitHub Actions):**
```yaml
- name: Configure Conan remotes
  run: |
    conan remote add conan-rc "${{ secrets.CONAN_RC_URL }}"
    conan remote add conan-stable "${{ secrets.CONAN_STABLE_URL }}"
    conan remote login conan-rc "${{ secrets.CONAN_USERNAME }}" -p "${{ secrets.CONAN_PASSWORD }}"
```

---

## How They Work Together

### Complete Build Flow

```
┌─────────────────────────────────────────────────────┐
│ 1. Developer writes C++ code                        │
│    └─ src/sum.cpp, include/mylib/sum.h             │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│ 2. CMakeLists.txt defines build rules               │
│    └─ add_library(mylib), enable_testing()         │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│ 3. conanfile.py defines dependencies                │
│    └─ requires = "gtest/1.14.0"                     │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│ 4. Conan installs dependencies                      │
│    $ conan install . --build=missing                │
│    └─ Downloads gtest from conancenter              │
│    └─ Generates CMakeToolchain, CMakeDeps           │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│ 5. CMake configures build                           │
│    $ cmake --preset conan-release                   │
│    └─ Uses Conan-generated toolchain                │
│    └─ Finds gtest via CMakeDeps                     │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│ 6. CMake builds project                             │
│    $ cmake --build --preset conan-release           │
│    └─ Compiles src/sum.cpp                          │
│    └─ Links with gtest                              │
│    └─ Creates libmylib.a (Linux) or mylib.lib (Win)│
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│ 7. Conan creates package                            │
│    $ conan create . --version=3.0.0-dev-7fcce98     │
│    └─ Packages compiled library                     │
│    └─ Creates mylib/3.0.0-dev-7fcce98               │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│ 8. Upload to JFrog (conan-rc)                       │
│    $ conan upload mylib/3.0.0-dev-7fcce98 \         │
│      --remote=conan-rc                              │
│    └─ Team can test this RC version                 │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓ (After testing passes)
┌─────────────────────────────────────────────────────┐
│ 9. Build clean release & upload to conan-stable     │
│    $ conan create . --version=3.0.0                 │
│    $ conan upload mylib/3.0.0 --remote=conan-stable │
│    └─ Production-ready release!                     │
└─────────────────────────────────────────────────────┘
```

---

## Real World Example

### Project Structure

```
math_utilities/
├── CMakeLists.txt          # CMake build configuration
├── conanfile.py            # Conan package definition
├── VERSION                 # 3.0.0
├── profiles/               # Platform-specific Conan settings
│   ├── linux               # gcc configuration
│   ├── macos               # clang configuration
│   └── windows             # MSVC configuration
├── src/
│   └── sum.cpp             # Implementation
├── include/
│   └── mylib/
│       └── sum.h           # Public API
└── tests/
    └── test_sum.cpp        # Unit tests using gtest
```

### Step-by-Step: Building mylib

#### Step 1: Install Dependencies

```bash
$ conan install . --profile=profiles/linux --build=missing
```

**What happens:**
1. Conan reads `conanfile.py`
2. Sees `requires = "gtest/1.14.0"`
3. Checks local cache (~/.conan2/)
4. Not found? Downloads from conancenter
5. Builds gtest for Linux + gcc
6. Generates `build/generators/`:
   - `CMakeDeps.cmake` (find gtest)
   - `conan_toolchain.cmake` (compiler settings)

**Output:**
```
Installing packages
  gtest/1.14.0: Already installed
Generating files:
  CMakeToolchain.cmake
  CMakeDeps.cmake
```

#### Step 2: Configure with CMake

```bash
$ cmake --preset conan-release
```

**What happens:**
1. CMake reads `CMakeLists.txt`
2. Loads `conan_toolchain.cmake` (Conan settings)
3. Loads `CMakeDeps.cmake` (finds gtest)
4. Configures build for Release mode
5. Creates native build files (Makefile on Linux)

**Output:**
```
-- The C compiler identification is GNU 11.4.0
-- Detecting C++ compiler ABI info - done
-- Found GTest: gtest/1.14.0
-- Configuring done
-- Generating done
```

#### Step 3: Build

```bash
$ cmake --build --preset conan-release
```

**What happens:**
1. Compiles `src/sum.cpp` → `sum.o`
2. Links into `libmylib.a` (Linux) or `mylib.lib` (Windows)
3. Compiles `tests/test_sum.cpp`
4. Links with `libmylib.a` + `libgtest.a` → test executable

**Output:**
```
[ 50%] Building CXX object src/CMakeFiles/mylib.dir/sum.cpp.o
[100%] Linking CXX static library libmylib.a
```

#### Step 4: Test

```bash
$ ctest --test-dir build
```

**What happens:**
1. Runs test executable
2. gtest runs your test cases
3. Reports pass/fail

**Output:**
```
Test project build
    Start 1: SumTest
1/1 Test #1: SumTest ..........................   Passed    0.01 sec

100% tests passed, 0 tests failed
```

#### Step 5: Package with Conan

```bash
$ conan create . --version=3.0.0-dev-7fcce98
```

**What happens:**
1. Creates clean build in temp folder
2. Runs all build steps (install → configure → build → test)
3. Packages result:
   - `include/mylib/sum.h` → package include/
   - `libmylib.a` → package lib/
4. Saves to local cache: `~/.conan2/p/mylib/3.0.0-dev-7fcce98/`

**Output:**
```
mylib/3.0.0-dev-7fcce98: Exporting package recipe
mylib/3.0.0-dev-7fcce98: Building from source
mylib/3.0.0-dev-7fcce98: Package built!
```

#### Step 6: Upload to JFrog

```bash
$ conan upload mylib/3.0.0-dev-7fcce98 --remote=conan-rc
```

**What happens:**
1. Authenticates with JFrog
2. Uploads package metadata (conanfile.py)
3. Uploads binaries (libmylib.a for Linux/gcc/Release)
4. Now available to your team!

**Output:**
```
Uploading mylib/3.0.0-dev-7fcce98 to conan-rc
Uploaded conanfile.py
Uploaded package binaries
```

#### Step 7: Use in Another Project

```bash
# In consumer project
$ conan install --requires=mylib/3.0.0-dev-7fcce98 --remote=conan-rc
```

**What happens:**
1. Conan queries conan-rc remote
2. Downloads mylib package
3. Generates CMake files to find it
4. Your project can now `find_package(mylib)`

**CMakeLists.txt:**
```cmake
find_package(mylib CONFIG REQUIRED)
add_executable(app main.cpp)
target_link_libraries(app mylib::mylib)
```

---

## Key Takeaways

### CMake
- ✅ **Cross-platform build system** - Write once, build anywhere
- ✅ **Abstracts compiler differences** - Same commands on all OS
- ✅ **Dependency management** - Links libraries correctly
- ✅ **Testing integration** - Built-in ctest support

### Conan
- ✅ **Package manager** - Like npm/pip for C++
- ✅ **Automatic dependency resolution** - Downloads + builds
- ✅ **Binary packages** - Pre-compiled for your platform
- ✅ **Version control** - Pin exact versions
- ✅ **CMake integration** - Generates toolchains automatically

### JFrog Artifactory
- ✅ **Package hosting** - Central storage for team
- ✅ **Version management** - Multiple versions side-by-side
- ✅ **Access control** - Private packages for your org
- ✅ **Binary storage** - Compiled libraries, not source
- ✅ **CI/CD integration** - Automated uploads from GitHub Actions

### Why All Three?

```
CMake:    Knows how to BUILD your code
          (compiles .cpp → .a/.lib)

Conan:    Knows how to PACKAGE your code
          (bundles .a + .h → shareable package)

JFrog:    Knows how to STORE packages
          (central repo for your team)
```

**Together:** A complete solution for building, packaging, and distributing cross-platform C++ libraries! 🚀

---

## Further Reading

- **CMake Tutorial:** https://cmake.org/cmake/help/latest/guide/tutorial/
- **Conan Documentation:** https://docs.conan.io/2/
- **JFrog Artifactory:** https://jfrog.com/artifactory/
- **This Project's README:** [README.md](README.md)
