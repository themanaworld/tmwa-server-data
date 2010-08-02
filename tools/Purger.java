/*
 * Purger (c) 2006 Eugenio Favalli
 * License: GPL, v2 or later
 */
 
import java.io.*; 
import java.text.*;
import java.util.*;

 public class Purger {

    public static void main(String[] args) {
        if (args.length != 2) {
            System.err.println(
                "Usage: java Purger <folder> <date>\n" +
                " - folder: is the path to account.txt and athena.txt files.\n" +
                " - date: accounts created before this date will be purged (dd/mm/yy or yyyy-mm-dd).");
            return;
        }

        int accounts = 0;
        int characters = 0;
        int deletedCharacters = 0;
        Vector activeAccounts = new Vector();

        File folder = new File(args[0]);
        // Do some sanity checking
        if (!folder.exists()) {
            System.err.println("Folder does not exist!");
            return;
        }
        if (!folder.isDirectory()) {
            System.err.println("Folder is not a folder!");
            return;
        }

        File oldAccount = new File(folder, "account.txt");
        File oldAthena = new File(folder, "athena.txt");
        File newAccount = new File(folder, "account.txt.new");
        File newAthena = new File(folder, "athena.txt.new");

        DateFormat dateFormat;
        Date purgeDate = null;

        for (String format : new String[] {"dd/MM/yy", "yyyy-MM-dd"}) {
            dateFormat = new SimpleDateFormat(format);

            try {
                purgeDate = dateFormat.parse(args[1]);
                break;
            } catch (ParseException e) {}
        }

        if (purgeDate == null) {
            System.err.println("ERROR: Date format not recognized.");
            return;
        }
        
        System.out.printf("Removing accounts unused since %tF\n", purgeDate);

        String line;

        // Remove accounts
        try {
            FileInputStream fin =  new FileInputStream(oldAccount);
            BufferedReader input = new BufferedReader(
                    new InputStreamReader(fin));
            FileOutputStream fout = new FileOutputStream(newAccount);
            PrintStream output = new PrintStream(fout);

            while ((line = input.readLine()) != null) {
                boolean copy = false;
                String[] fields = line.split("\t");
                // Check if we're reading a comment or the last line
                if (line.substring(0, 2).equals("//") || fields[1].charAt(0) == '%') {
                    copy = true;
                }
                else {
                    // Server accounts should not be purged
                    if (fields[4].equals("S")) {
                        copy = true;
                    } else {
                        accounts++;
                        dateFormat = new SimpleDateFormat("yyyy-MM-dd");
                        try {
                            Date date = dateFormat.parse(fields[3]);
                            if (date.after(purgeDate)) {
                                activeAccounts.add(fields[0]);
                                copy = true;
                            }
                            else
                            {
                                System.out.println("Removing " + fields[1]);
                            }
                        }
                        catch (ParseException e) {
                            // Ignore accounts that haven't been used yet
                            if (fields[3].equals("-")) {
                                activeAccounts.add(fields[0]);
                                copy = true;
                            }
                            else {
                                System.err.println("ERROR: Wrong date format in account.txt. (" + accounts + ": " + line + ")");
                                System.out.println("Removing " + fields[1]);
                            }
                        }
                        catch (Exception e) {
                            e.printStackTrace();
                            return;
                        }
                    }
                }
                if (copy) {
                    try {
                        output.println(line);
                    }
                    catch (Exception e) {
                        System.err.println("ERROR: Unable to write file.");
                    }
                }
            }
            input.close();
            output.close();
        }
        catch (FileNotFoundException e ) {
            System.err.println("ERROR: file " + oldAccount.getAbsolutePath() + " not found.");
            return;
        }
        catch (Exception e) {
            System.err.println("ERROR: unable to process account.txt");
            e.printStackTrace();
            return;
        }

        System.out.println("Removed " + (accounts - activeAccounts.size()) + "/" + accounts + " accounts.");

        // Remove characters
        try {
            FileInputStream fin =  new FileInputStream(oldAthena);
            BufferedReader input = new BufferedReader(
                    new InputStreamReader(fin));
            FileOutputStream fout = new FileOutputStream(newAthena);
            PrintStream output = new PrintStream(fout);

            while ((line = input.readLine()) != null) {
                boolean copy = false;
                String[] fields = line.split("\t");
                // Check if we're reading a comment or the last line
                if (line.substring(0, 2).equals("//")
                        || fields[1].charAt(0) == '%') {
                    copy = true;
                }
                else {
                    characters++;
                    String id = fields[1].substring(0, fields[1].indexOf(','));
                    if (activeAccounts.contains(id)) {
                        copy = true;
                    }
                    else {
                        deletedCharacters++;
                    }
                }
                if (copy) {
                    output.println(line);
                }
            }
            input.close();
            output.close();
        }
        catch (FileNotFoundException e ) {
            System.err.println("ERROR: file " + oldAthena.getAbsolutePath() + " not found.");
            return;
        }
        catch (Exception e) {
            System.err.println("ERROR: unable to process athena.txt");
            e.printStackTrace();
            return;
        }

        System.out.println(
            "Removed " + deletedCharacters + "/"
            + characters + " characters.");
    }
    
}

