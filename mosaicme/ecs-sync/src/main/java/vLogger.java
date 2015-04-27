import org.apache.log4j.Logger;

public class vLogger {

		
	   public static void main(String[] args) {
		      LogTrace("Trace Message!");
		      LogDebug("Debug Message!");
		      LogInfo("Info Message!");
		      LogWarn("Warn Message!");
		      LogError("Error Message!");
		      LogFatal("Fatal Message!");
		   }
	   
	public static void LogTrace(String msg) {
		// TODO Auto-generated method stub
		org.apache.log4j.Logger log = org.apache.log4j.Logger.getLogger(vLogger.class);
		log.trace(msg);
	}

	public static void LogDebug(String msg) {
		// TODO Auto-generated method stub
		org.apache.log4j.Logger log = org.apache.log4j.Logger.getLogger(vLogger.class);
		log.debug(msg);
	}

	public static void LogInfo(String msg) {
		// TODO Auto-generated method stub
		org.apache.log4j.Logger log = org.apache.log4j.Logger.getLogger(vLogger.class);
		log.info(msg);
	}
	
	public static void LogWarn(String msg) {
		org.apache.log4j.Logger log = org.apache.log4j.Logger.getLogger(vLogger.class);
		// TODO Auto-generated method stub
		log.warn(msg);
	}
	
	public static void LogError(String msg) {
		
		// TODO Auto-generated method stub
		org.apache.log4j.Logger log = org.apache.log4j.Logger.getLogger(vLogger.class);
		log.error(msg);
	}
	
	public static void LogFatal(String msg) {
		// TODO Auto-generated method stub
		org.apache.log4j.Logger log = org.apache.log4j.Logger.getLogger(vLogger.class);
		log.fatal(msg);
	}
	

}
