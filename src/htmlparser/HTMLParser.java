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
                System.out.println("Testing page " + page + "\n\n");
                response = Jsoup.connect("https://www.sobeys.com/en/flyer?&page=" + page)
                        .userAgent("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1042.0 Safari/535.21")
                        .timeout(20000)
                        .ignoreHttpErrors(true)
                        .execute();
                int statusCode = response.statusCode();
                if(statusCode != 200) { isPageThere = false; }
                else {
                    doc = Jsoup.connect("https://www.sobeys.com/en/flyer?&page=" + page).timeout(20000).get();
                    Elements body = doc.getElementsByClass("card-inset");
                    boolean isBodyEmpty = true;
                    for ( Element e : body ) {
                    	// only consider classes that contain the subclass 'price'
                    	// other classes could be named 'card-inset' - only products will have a price
                        if (e.children().hasClass("price")) {
                        	Document eDoc = Jsoup.parse(e.html());
                        	Element priceAmount = eDoc.select("div.price > div.price-amount").first();
                        	Element productName = eDoc.select("h6.x-small-bottom").first();
                        	Element productDesc = eDoc.select("p").first();
                        	Element productPromo = eDoc.select("div.price > ul.price-promos > li.price-promos-air-miles").first();
                        	String price = Jsoup.parse(priceAmount.html()).text();
                        	String name = Jsoup.parse(productName.html()).text();
                        	String desc = Jsoup.parse(productDesc.html()).text();
                        	String promo = null;
                        	if(productPromo != null) promo = Jsoup.parse(productPromo.html()).text();
                        	String[] split = null;
                        	if(!price.equals("")) {
                        		split = price.split("/");
                        	}
                        	
                        	if(price.contains("ea.")) {
                        		System.out.println(name + " are $" + split[0].replace(" ",  ".") + " each.");
                        	}
                        	else if(price.contains("lb.")) {
                        		System.out.println(name + " is $" + split[0].replace(" ", ".") + " per pound.");
                        	}
                        	else if(price.contains("g")) {
                        		System.out.println(name + " is $" + split[0].replace(" ", ".") + " per " + split[1].replace("g", "") + " grams.");
                        	}
                        	else if(split != null){ // of the form '2/1 00' meaning 2 for $1.00
                        		System.out.println(name + " is $" + split[1].replace(" ", ".") + " for " + split[0]);
                        	}
                        	else if(promo != null && desc.contains("BUY") && desc.contains("EARN")) { // has a points promotion rather than sale
                        		String promotion = desc.substring(desc.indexOf("BUY"), desc.length());
                        		System.out.println(name + " has a promotion: " + promotion);
                        	}
                        	else {
                        		System.out.println("\n\n\n\nNOTHING FOUND\n\n\n\n");
                        	}
                        	//System.out.println(e.html());
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
