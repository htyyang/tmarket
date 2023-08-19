class error:
    
    class URLNavigationError(Exception):
        pass

    class UnknownDriverError(Exception):
        pass
    
    class LoggerError:

        class LoggerMainError(Exception):
            pass
        
        class LoggerCreateError(LoggerMainError):
            pass

        class LoggerClearError(LoggerMainError):
            pass

        class LoggerSaveError(LoggerMainError):
            pass