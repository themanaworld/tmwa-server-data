/*
 * TMWServ to eAthena Converter (c) 2008 Jared Adams
 * License: GPL, v2 or later
 */

import java.io.*;
import java.lang.reflect.*;
import java.net.*;
import java.util.*;

public abstract class Converter {
    static String[] tiledJars = {"tiled-core.jar", "tiled.jar"};
    static String[] wlkJars = {"plugins/tmw.jar", "tmw.jar"};

    public static void main(String[] args) throws Exception {
        List<URL> urls = new ArrayList<URL>();

        File tiled = null;
        for (String s : tiledJars) {
            tiled = new File(s);
            if (tiled.exists()) break;
        }
        if (tiled == null || !tiled.exists()) {
            System.err.println("Unable to find a Tiled jar file! Exiting.");
            System.exit(-5);
        }
        urls.add(tiled.toURI().toURL());

        File wlkWriter = null;
        for (String s : wlkJars) {
            wlkWriter = new File(s);
            if (wlkWriter.exists()) break;
        }
        if (wlkWriter == null || !wlkWriter.exists()) {
            System.err.println("Unable to find the tmw plugin for Tiled! No wlk files will be made!");
        } else {
            urls.add(wlkWriter.toURI().toURL());
        }

        File self = new File("converter.jar");
        if (!self.exists()) {
            System.err.println("Unable to find a the converter jar! Exiting.");
            System.exit(-5);
        }
        urls.add(self.toURI().toURL());

        URLClassLoader loader = new URLClassLoader(urls.toArray(new URL[0]));
        Class c = loader.loadClass("converter.Main");
        Method m = c.getMethod("run", String[].class, Integer.TYPE);
        System.out.println("Starting");
        
        m.invoke(null, args, 0);
    }
}
