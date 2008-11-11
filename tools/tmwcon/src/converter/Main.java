//

package converter;

import java.io.*;
import java.util.*;

import tiled.io.xml.*;

public class Main extends Thread {
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

    public static void run(String[] args, int unused) {
        reader = new XMLMapTransformer();

        PrintWriter summary = null;

        try {
            File temp = new File("summary.txt");
            temp.createNewFile();
            summary = new PrintWriter(temp);
        } catch (Exception e) {
            System.out.println("Problem opening summary file for writing:");
            e.printStackTrace();
        }

        File folder = new File("server-data/data/");
        Process.prepWLK(folder);

        folder = new File("tmwdata/maps/");

        Collection<File> tmxs = getTMXFiles(folder);
        String name;
        for (File f : tmxs) {
            name = getName(folder, f);
            System.out.printf("== %s ==\n", name);
            if (summary != null) summary.printf("== %s ==\n", name);
            Process.processMap(name, loadMap(f), summary);
        }

        if (summary != null) {
            summary.flush();
            summary.close();
        }
    }

    public static void main(String[] args) {
        run(args, 0);
    }
}
