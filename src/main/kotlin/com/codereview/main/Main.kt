package com.codereview.main

import com.codereview.cli.CliMain
import com.codereview.gui.main

fun main(args: Array<String>) {
    if (args.isEmpty()) {
        // Launch GUI
        main()
    } else {
        // CLI mode
        CliMain().main(args)
    }
}