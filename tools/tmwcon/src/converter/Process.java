/*
 * Converter from Tiled .tmx files to tmwAthena .wlk and mob/warp scripts
 * Copyright (c) 2008, 2011 Jared Adams
 * Copyright (c) 2011 Ben Longbons
 * License: GNU GPL, v2 or later
 */

package converter;

import java.awt.*;
import java.io.*;
import java.util.Iterator;
import java.util.Properties;
import java.util.TreeSet;
import java.util.ArrayList;
import java.util.List;
import java.util.Collections;

import tiled.core.*;
import tiled.plugins.tmw.*;

public class Process {
    // both were formerly (hard-coded) "\t", for different reasons
    // Note: don't use println, as we want only '\n'
    private static final String SEPARATOR = "|";
    private static final String INDENTATION = "    ";

    private static final String mobFile = "_mobs.txt";
    private static final String warpFile = "_warps.txt";
    private static final String importFile = "_import.txt";
    private static File server_data;
    private static File script_directory;
    private static File wlkFolder;

    private static WLKInterface wlk = null;

    public static void setServerData(File folder) {
        server_data = folder;
        script_directory = new File(server_data, "npc/");
        wlkFolder = new File(server_data, "data/");
        wlk = new WLKInterface();
    }

    private static String getProp(Properties props, String name, String def) {
        if (name == null) return def;
        for (java.util.Map.Entry<Object, Object> entry : props.entrySet()) {
            if (name.equalsIgnoreCase(entry.getKey().toString())) {
                return entry.getValue().toString();
            }
        }
        return def;
    }

    private static int getProp(Properties props, String name, int def) {
        if (name == null) return def;
        try {
            return Integer.parseInt(getProp(props, name, "?"));
        } catch (Exception e) {}
        return def;
    }

    private static int[] resolveBounds(Rectangle in, boolean warp) {
        int x = in.x / 32;
        int y = in.y / 32;
        int width = in.width / 32;
        int height = in.height / 32;
        if (!warp) {
            if (width > 1) --width;
            if (height > 1) --height;
        }
        x += width / 2;
        y += height / 2;
        if (warp) {
            width -= 2;
            height -= 2;
        }
        return new int[]{x, y, width, height};
    }

    private static void handleWarp(PrintWriter out, String map, String name, Rectangle bounds, Properties props) {
        if (out == null) return;
        String dest = getProp(props, "dest_map", null);
        if (dest == null) return;
        int x = getProp(props, "dest_x", -1);
        if (x < 0) return;
        int y = getProp(props, "dest_y", -1);
        if (y < 0) return;
        int[] shape = resolveBounds(bounds, true);
        System.out.printf("Usable warp found: %s\n", name);
        out.printf("%s.gat,%d,%d" + SEPARATOR + "warp" + SEPARATOR + "%s" + SEPARATOR + "%d,%d,%s.gat,%d,%d\n",
                   map, shape[0], shape[1], name, shape[2], shape[3], dest, x / 32, y / 32);
    }

    private static int handleMob(PrintWriter out, String map, String name, Rectangle bounds, Properties props) {
        if (out == null) return -1;
        int mob = getProp(props, "monster_id", -1);
        if (mob < 0) return -1;
        mob += 1002;
        int max = getProp(props, "max_beings", 1);
        int time1 = getProp(props, "eA_spawn", 0);
        int time2 = getProp(props, "eA_death", 0);
        int[] shape = resolveBounds(bounds, false);
        System.out.printf("Usable mob found: %s (%d)\n", name, mob);
        out.printf("%s.gat,%d,%d,%d,%d" + SEPARATOR + "monster" + SEPARATOR + "%s" + SEPARATOR + "%d,%d,%d,%d,Mob%s::On%d\n",
                   map, shape[0], shape[1], shape[2], shape[3], name, mob, max, time1, time2, map, mob);
        return mob;
    }

    private static void processObject(MapObject mo, String map, PrintWriter warpOut, PrintWriter mobOut, TreeSet<Integer> mobs) {
        if (mo == null) return;
        String name = mo.getName();
        String type = mo.getType();
        Rectangle bounds = new Rectangle(mo.getBounds());
        Properties props = mo.getProperties();

        if (type.equalsIgnoreCase("warp")) {
            handleWarp(warpOut, map, name, bounds, props);
        } else if (type.equalsIgnoreCase("spawn")) {
            mobs.add(handleMob(mobOut, map, name, bounds, props));
        }
    }

    private static void processObjects(Iterator<MapObject> objs, String map, PrintWriter warpOut, PrintWriter mobOut, TreeSet<Integer> mobs) {
        MapObject mo;
        while (objs.hasNext()) {
            mo = objs.next();
            if (mo == null) continue;
            processObject(mo, map, warpOut, mobOut, mobs);
        }
    }

    private static void processFiles(File folder, List<String> out) {
        for (File f : folder.listFiles()) {
            if (f.isDirectory()) {
                processFiles(folder, out);
            } else if (!f.getName().equals(importFile)) {
                out.add("npc: " + f.getPath().substring(server_data.getPath().length() + 1));
            }
        }
    }

    private static void makeInclude(String name, String title, File folder) {
        File _import = new File(folder, importFile);
        List<String> output_elements = new ArrayList<String>();
        processFiles(folder, output_elements);
        PrintWriter importOut = Main.getWriter(_import);
        importOut.printf("// Map %s: %s\n", name, title);
        importOut.print("// This file is generated automatically. All manually changes will be removed when running the Converter.\n");
        importOut.printf("map: %s.gat\n", name);
        Collections.sort(output_elements);
        for (String s : output_elements)
            if (!s.endsWith("~"))
            importOut.print(s + "\n");
        importOut.flush();
        importOut.close();
    }

    public static String processMap(String name, Map map, File mapFile, PrintWriter summary) {
        if (name == null) return null;
        if (map == null) return null;

        Properties props = map.getProperties();
        String title = getProp(props, "name", "unnamed map " + name);

        String folderName =  "npc/" + name;

        File folder = new File(script_directory, name);

        System.out.println(title);

        File wlkFile = new File(wlkFolder, name + ".wlk");

        if (wlkFile.exists() && mapFile.lastModified() < wlkFile.lastModified()) {
            System.out.println("Up to date, skipping");
            makeInclude(name, title, folder);
            return folderName;
        }

        if (summary != null) {
            summary.printf("Name: %s: '%s'\n", name, title);
            summary.printf("Music: '%s'\n", getProp(props, "music", ""));
            summary.printf("Minimap: '%s'\n", getProp(props, "minimap", ""));
        }

        if (wlk != null) wlk.write(name, map, wlkFile);

        PrintWriter warpOut = Main.getWriter(new File(folder, warpFile));
        PrintWriter mobOut = Main.getWriter(new File(folder, mobFile));

        warpOut.print("// This file is generated automatically. All manually changes will be removed when running the Converter.\n");
        warpOut.printf("// %s warps\n\n", title);
        mobOut.print("// This file is generated automatically. All manually changes will be removed when running the Converter.\n");
        mobOut.printf("// %s mobs\n\n", title);

        TreeSet<Integer> mobs = new TreeSet<Integer>();
        processObjects(map.getObjects(), name, warpOut, mobOut, mobs);
        for (MapLayer layer : map) {
            if (layer instanceof ObjectGroup) {
                processObjects(((ObjectGroup) layer).getObjects(), name, warpOut, mobOut, mobs);
            }
        }

        warpOut.flush();
        warpOut.close();

        System.out.println("Starting mob points");
        mobOut.printf("\n\n%s.gat,0,0,0" + SEPARATOR + "script" + SEPARATOR + "Mob%1$s" + SEPARATOR + "-1,{\n", name);
        for (int mob : mobs) {
            if (mob == -1) continue;
            mobOut.printf("On%d:\n", mob);
            mobOut.printf(INDENTATION + "set @mobID, %d;\n", mob);
            mobOut.printf(INDENTATION + "callfunc \"MobPoints\";\n");
            mobOut.printf(INDENTATION + "end;\n\n");
        }
        mobOut.printf(INDENTATION + "end;\n}\n");
        System.out.println("Finished mob points");

        mobOut.flush();
        mobOut.close();

        makeInclude(name, title, folder);

        return folderName;
    }

    public static void writeMasterImport(ArrayList<String> folders) {
        File master = new File(script_directory, importFile);
        PrintWriter out = Main.getWriter(master);
        if (out == null) return;

        List<String> output_elements = new ArrayList<String>();

        output_elements.add("// This file is generated automatically. All manually changes will be removed when running the Converter.\n");
        for (String folder : folders) {
            if (folder == null) continue;
            output_elements.add("import: " + folder + "/_import.txt");
        }

        Collections.sort(output_elements);
        for (String s : output_elements)
            out.print(s + "\n");

        out.flush();
        out.close();
    }
}
