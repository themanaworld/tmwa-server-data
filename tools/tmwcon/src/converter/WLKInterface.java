//

package converter;

import java.io.*;

import tiled.core.*;
import tiled.plugins.tmw.*;

public class WLKInterface {
    private File folder;
    public WLKInterface(File folder) {
        WLKWriter.class.getName();
        this.folder = folder;
        File f = new File("server-data/data");
        f.mkdirs();
    }

    public void write(String name, Map map) {
        File wlk = new File(folder, name + ".wlk");

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
