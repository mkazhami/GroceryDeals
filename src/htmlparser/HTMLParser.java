/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package htmlparser;

import java.io.IOException;
import java.io.PrintWriter;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.jsoup.nodes.Document;
import org.jsoup.*;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import com.gargoylesoftware.htmlunit.BrowserVersion;
import com.gargoylesoftware.htmlunit.FailingHttpStatusCodeException;
import com.gargoylesoftware.htmlunit.HttpWebConnection;
import com.gargoylesoftware.htmlunit.NicelyResynchronizingAjaxController;
import com.gargoylesoftware.htmlunit.WebClient;
import com.gargoylesoftware.htmlunit.WebRequest;
import com.gargoylesoftware.htmlunit.WebResponse;
import com.gargoylesoftware.htmlunit.WebWindow;
import com.gargoylesoftware.htmlunit.html.HtmlAnchor;
import com.gargoylesoftware.htmlunit.html.HtmlDivision;
import com.gargoylesoftware.htmlunit.html.HtmlPage;
import com.gargoylesoftware.htmlunit.javascript.background.JavaScriptJobManager;
import com.gargoylesoftware.htmlunit.util.NameValuePair;
import com.gargoylesoftware.htmlunit.Page;


/**
 *
 * @author mkazhamiaka
 */
public class HTMLParser {

    /**
     * @param args the command line arguments
     * @throws InterruptedException 
     */
    public static void main(String[] args) throws InterruptedException {
    	WebClient wc = new WebClient();
    	Document zehrsDoc = null;
    	try {
			//zehrsDoc = Jsoup.connect("http://www.zehrs.ca/en_CA/flyers.banner@ZEHRS.storenum@550.html").userAgent("Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.120 Safari/535.2").get();
    		//String zehrsPage = new WebClient(BrowserVersion.CHROME).getPage("http://www.zehrs.ca/en_CA/flyers.banner@ZEHRS.storenum@550.html").getWebResponse().getContentAsString();
    		WebClient webClient = new WebClient(BrowserVersion.FIREFOX_38);
    		webClient.getOptions().setJavaScriptEnabled(true);
    		webClient.getOptions().setCssEnabled(false);
    		webClient.getOptions().setThrowExceptionOnScriptError(false);
    		webClient.setJavaScriptTimeout(30000);
    		webClient.getCookieManager().setCookiesEnabled(true);
    		webClient.setAjaxController(new NicelyResynchronizingAjaxController());
    		webClient.getWebConnection().
    		
    		WebWindow ww = webClient.openWindow(new URL("http://www.zehrs.ca/en_CA/flyers.accessibleview.banner@ZEHRS.storenum@550.week@current.html"), "zehrs");
    		Thread.sleep(10000);
    		HtmlPage p = (HtmlPage) ww.getEnclosedPage();
    		//System.out.println(p.asXml());
    		HtmlPage page = webClient.getPage("http://www.zehrs.ca/en_CA/flyers.accessibleview.banner@ZEHRS.storenum@550.week@current.html");

    		webClient.waitForBackgroundJavaScript(10000);
    		
    		List<NameValuePair> response = page.getWebResponse().getResponseHeaders();
    		for (NameValuePair header : response) {
    			System.out.println(header.getName() + " = " + header.getValue());
    		}
    		
    		PrintWriter writer = new PrintWriter("zehrsPage.txt", "UTF-8");
    		writer.println(page.asXml());
    		//writer.println(zehrsDoc.html());
    		writer.close();
    		//System.out.println(page.asXml());
		} catch (FailingHttpStatusCodeException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		} catch (MalformedURLException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		} catch (IOException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
    	
    	/*
        Document sobeysDoc = null;
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
                    sobeysDoc = Jsoup.connect("https://www.sobeys.com/en/flyer?&page=" + page).timeout(20000).get();
                    Elements body = sobeysDoc.getElementsByClass("card-inset");
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
        }*/
    }
    
}
