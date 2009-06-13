/*
 * TMWServ to eAthena Converter (c) 2008 Jared Adams
 * License: GPL, v2 or later
 */

package converter;

import java.io.*;

import tiled.core.*;
import tiled.plugins.tmw.*;

public class WLKInterface {
    public WLKInterface() {
        // See if the writer is available
        WLKWriter.class.getName();
    }

    public void write(String name, Map map, File wlk) {
        try {
            wlk.createNewFile();
            WLKWriter.writeMap(map, new FileOutputStream(wlk));
            System.out.println("WLK written");
        } catch (Exception e) {
            System.out.println("Prolem writing WLK file:");
            e.printStackTrace();
        }
    }
}
