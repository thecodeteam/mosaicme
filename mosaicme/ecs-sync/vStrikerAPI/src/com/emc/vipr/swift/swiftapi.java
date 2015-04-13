package com.emc.vipr.swift;

import org.javaswift.joss.client.factory.AccountConfig;
import org.javaswift.joss.client.factory.AccountFactory;
import org.javaswift.joss.model.Account;
import org.javaswift.joss.model.Container;
import org.javaswift.joss.model.StoredObject;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;

public class swiftapi {

	public static Account ViPRSwiftClient(String username,String password,String dataNode)throws Exception
		{
			try {
				AccountConfig config = new AccountConfig();
				config.setUsername(username);
				config.setPassword(password);
				config.setAuthUrl(dataNode + "/v2.0/tokens");
				config.setDisableSslValidation(true);
				Account account = new AccountFactory(config).createAccount();
				return account;
			} catch (Exception e) {
				System.out.println("error during creating connection with " + dataNode);
				e.printStackTrace();
			}
			return null;
		}

		public static void CreateObject(String username,String passwod,String dataNode, String container, String key, InputStream content)throws Exception
		{
			try{
				Account client = ViPRSwiftClient(username, passwod, dataNode);
				Container myContainer = client.getContainer(container);
				StoredObject object = myContainer.getObject(key);
				object.uploadObject(content);
			}
			catch(Exception e)
			{
				System.out.println("error during creating "+key);
				e.printStackTrace();
			}

		}

		public static InputStream ReadObject(String username,String passwod,String dataNode, String container, String key)throws Exception {
			try {
				Account client = ViPRSwiftClient(username, passwod, dataNode);
				Container myContainer = client.getContainer(container);
				StoredObject object = myContainer.getObject(key);
				return object.downloadObjectAsInputStream();
			} catch (Exception e) {
				System.out.println("error during reading " + key);
				e.printStackTrace();
			}
			return null;
		}

		public static void DeleteObject(String username,String passwod,String dataNode, String container, String key)throws Exception {
			try {
				Account client = ViPRSwiftClient(username, passwod, dataNode);
				Container myContainer = client.getContainer(container);
				StoredObject object = myContainer.getObject(key);
				object.delete();

			} catch (Exception e) {
				System.out.println("error during delete " + key);
				e.printStackTrace();
			}
		}

	
}
