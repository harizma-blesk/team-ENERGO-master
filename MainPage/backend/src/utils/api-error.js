export const errorResponse = (code, message, traceId, details) => ({
  error: {
    code,
    message,
    details,
    traceId,
    timestamp: new Date().toISOString()
  }
});
