#!/bin/bash

#----SCAFFOLD FUNCTION----

scaffold() {
    # --- CONFIG ---
    local TEMPLATE_PATH="$HOME/.config/cp-templates/main.cpp"
    # ---

    if [ "$#" -ne 1 ]; then
        echo "Usage: scaffold <directory_name>"
        return 1
    fi

    local DIR_NAME=$1

    if ! mkdir "$DIR_NAME"; then
        echo "Error: Directory $DIR_NAME already exists or couldn't be created."
        return 1
    fi

    cd "$DIR_NAME"

    if [ -f "$TEMPLATE_PATH" ]; then
        cp "$TEMPLATE_PATH" "main.cpp"
    else
        touch "main.cpp"
    fi

    touch "input.txt"
    echo "Done. Scaffolding complete in $(pwd)"
}


#----TEST FUNCTION----

test() {
    # --- CONFIG ---
    local FILENAME="main.cpp"
    local INPUT_FILE="input.txt"
    local OUTPUT_BINARY="main"
    # C++ flags: -std=c++17, enable warnings, enable address sanitizer
    local COMPILE_FLAGS="-std=c++17 -Wall -g -fsanitize=address"
    # ---

    echo "--- Compiling $FILENAME... ---"

    # Compile the file
    if ! g++ $COMPILE_FLAGS "$FILENAME" -o "$OUTPUT_BINARY"; then
        echo "--- Compilation FAILED. ---"
        return 1 # Use 'return' in a function
    fi

    echo "--- Compilation SUCCESS. ---"
    echo ""
    echo "--- Running $OUTPUT_BINARY with $INPUT_FILE... ---"

    # Run the compiled binary, piping in the input.txt file
    ./"$OUTPUT_BINARY" < "$INPUT_FILE"

    echo ""
    echo "--- Execution FINISHED. ---"
}
