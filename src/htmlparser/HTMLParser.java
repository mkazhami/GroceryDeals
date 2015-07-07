/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package htmlparser;

import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.jsoup.nodes.Document;
import org.jsoup.*;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

/**
 *
 * @author mkazhamiaka
 */
public class HTMLParser {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        Document doc = null;
        int pageCount = 1;
        boolean isPageThere = true;
        while(isPageThere) {
            String page = Integer.toString(pageCount);
            Connection.Response response = null;
            try {
                System.out.println("Testing page " + page);
                response = Jsoup.connect("https://www.sobeys.com/en/flyer?&page=" + page)
                        .userAgent("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1042.0 Safari/535.21")
                        .timeout(10000)
                        .ignoreHttpErrors(true)
                        .execute();
                int statusCode = response.statusCode();
                if(statusCode != 200) { isPageThere = false; }
                else {
                    doc = Jsoup.connect("https://www.sobeys.com/en/flyer?&page=" + page).get();
                    Elements body = doc.getElementsByClass("card-inset");
                    boolean isBodyEmpty = true;
                    for ( Element e : body ) {
                        if (e.children().hasClass("price")) {
                            System.out.println(e.html() + "\n\n");
                            isBodyEmpty = false;
                        }
                    }
                    if(isBodyEmpty) { isPageThere = false; }
                    pageCount++;
                }
            } catch (Exception ex) {
                Logger.getLogger(HTMLParser.class.getName()).log(Level.SEVERE, null, ex);
                isPageThere = false;
            }
        }
    }
    
}
