/*
 * TMWServ to eAthena Converter (c) 2008 Jared Adams
 * License: GPL, v2 or later
 */

package converter;

import java.io.*;
import java.util.*;

import tiled.io.xml.*;

public class Main {
    public static XMLMapTransformer reader = null;

    private static tiled.core.Map loadMap(File file) {
        tiled.core.Map map = null;
        try {
            map = reader.readMap(file.getAbsolutePath());
        } catch (Exception e) {
            e.printStackTrace();
        }

        return map;
    }

    public static boolean isTMX(File in) {
        if (in.isDirectory()) return false;

        return in.getName().matches(".*\\.tmx(\\.gz)?$");
    }

    public static Collection<File> getTMXFiles(File directory) {
        if (!directory.isDirectory()) return Collections.emptyList();

        List<File> ret = new Vector<File>();

        for (File f : directory.listFiles()) {
            if (f.isDirectory()) {
                ret.addAll(getTMXFiles(f));
            } else if (isTMX(f)) {
                ret.add(f);
            }
        }

        return ret;
    }

    public static PrintWriter getWriter(File f) {
        try {
            f.getParentFile().mkdir();
            f.createNewFile();
            return new PrintWriter(f);
        } catch (Exception e) {
            e.printStackTrace();
        }

        return null;
    }

    public static String getName(File folder, File file) {
        String path = folder.getAbsolutePath();
        String name = file.getAbsolutePath();
        if (name.startsWith(path)) name = name.substring(path.length() + 1);
        if (name.endsWith(".gz")) name = name.substring(0, name.length() - 3);
        if (name.endsWith(".tmx")) name = name.substring(0, name.length() - 4);
        return name;
    }

    public static void main(String[] args) throws IOException {
        if (args.length != 2) {
            System.out.println("Usage: java Converter client-data-dir server-data-dir");
            System.exit(1);
        }

        File client_data = new File(args[0]);
        File server_data = new File(args[1]);

        reader = new XMLMapTransformer();

        PrintWriter summary = new PrintWriter("converter.txt");

        Process.setServerData(server_data);

        File folder = new File(client_data, "maps/");

        Collection<File> tmxs = getTMXFiles(folder);
        ArrayList<String> folders = new ArrayList<String>();
        String name;
        for (File f : tmxs) {
            name = getName(folder, f);
            System.out.printf("== %s ==\n", name);
            folders.add(Process.processMap(name, loadMap(f), f, summary));
        }

        summary.flush();
        summary.close();

        Process.writeMasterImport(folders);
    }
}
