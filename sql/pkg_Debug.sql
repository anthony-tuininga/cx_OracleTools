create or replace package pkg_Debug as

  /*---------------------------------------------------------------------------
   * DESCRIPTION
   *   Routines used to display output on a separate process for debugging
   * purposes.
   *-------------------------------------------------------------------------*/

  /*---------------------------------------------------------------------------
   * PipeName()
   *   Returns the pipe name to which debug output will be sent.
   *-------------------------------------------------------------------------*/
  function PipeName
  return varchar2;

  /*---------------------------------------------------------------------------
   * SetPipeName()
   *   Set the pipe name to which debug output will be sent.
   *-------------------------------------------------------------------------*/
  procedure SetPipeName (
    a_PipeName				varchar2
  );

  /*---------------------------------------------------------------------------
   * Enabled()
   *   Returns a boolean (single character "Y" or "N") indicating if debug is
   * currently enabled.
   *-------------------------------------------------------------------------*/
  function Enabled
  return varchar2;

  /*---------------------------------------------------------------------------
   * Suspended()
   *   Returns a boolean (single character "Y" or "N") indicating if debug is
   * currently suspended.
   *-------------------------------------------------------------------------*/
  function Suspended
  return varchar2;

  /*---------------------------------------------------------------------------
   * Enable()
   *   Enable debug output. If a pipename is specified that pipe will be used
   * to log future debug output; otherwise, the currently set pipename will be
   * used.
   *-------------------------------------------------------------------------*/
  procedure Enable (
    a_PipeName				varchar2 default null
  );

  /*---------------------------------------------------------------------------
   * Disable()
   *   Disable debug output.
   *-------------------------------------------------------------------------*/
  procedure Disable;

  /*---------------------------------------------------------------------------
   * Suspend()
   *   Suspend debugging. This can be reversed by resuming or enabling again.
   *-------------------------------------------------------------------------*/
  procedure Suspend;

  /*---------------------------------------------------------------------------
   * Resume()
   *   Resume debugging after a suspension.
   *-------------------------------------------------------------------------*/
  procedure Resume;

  /*---------------------------------------------------------------------------
   * Shutdown()
   *   Shutdown the session which is receiving debug output. If the pipename
   * is specified that pipename will be sent the shutdown message; otherwise,
   * the currently set pipename will be send the message.
   *-------------------------------------------------------------------------*/
  procedure Shutdown (
    a_PipeName				varchar2 default null
  );

  /*---------------------------------------------------------------------------
   * PutLine()
   *   Pass the given string to the debug output session.
   *-------------------------------------------------------------------------*/
  procedure PutLine (
    a_Message				varchar2
  );

  /*---------------------------------------------------------------------------
   * PutSingleLine()
   *   Put the line to the debug output session. If the session is not enabled
   * currently, it will be enabled long enough to output this line and then
   * disabled again.
   *-------------------------------------------------------------------------*/
  procedure PutSingleLine (
    a_Message				varchar2
  );

end pkg_Debug;
/

grant execute
on pkg_debug
to public;

create or replace package body pkg_Debug as

  /*---------------------------------------------------------------------------
   * Globals
   *-------------------------------------------------------------------------*/
  gc_ProtocolVersion			constant varchar2(30) := '2';
  g_PipeName				varchar2(30) := 'DbDebugger';
  g_Enabled				boolean := false;
  g_Suspended				boolean := false;
  g_TimeOut				number := 20;

  /*---------------------------------------------------------------------------
   * PipeName() -- PUBLIC
   *-------------------------------------------------------------------------*/
  function PipeName
  return varchar2 is
  begin
    return g_PipeName;
  end;

  /*---------------------------------------------------------------------------
   * SetPipeName() -- PUBLIC
   *-------------------------------------------------------------------------*/
  procedure SetPipeName (
    a_PipeName				varchar2
  ) is
  begin
    g_PipeName := a_PipeName;
  end;

  /*---------------------------------------------------------------------------
   * Enabled() -- PUBLIC
   *-------------------------------------------------------------------------*/
  function Enabled
  return varchar2 is
  begin
    if g_Enabled then
      return 'Y';
    end if;
    return 'N';
  end;

  /*---------------------------------------------------------------------------
   * Suspended() -- PUBLIC
   *-------------------------------------------------------------------------*/
  function Suspended
  return varchar2 is
  begin
    if g_Suspended then
      return 'Y';
    end if;
    return 'N';
  end;

  /*---------------------------------------------------------------------------
   * Enable() -- PUBLIC
   *-------------------------------------------------------------------------*/
  procedure Enable (
    a_PipeName				varchar2
  ) is
  begin
    g_Enabled := true;
    g_Suspended := false;
    if a_PipeName is not null then
      g_PipeName := a_PipeName;
    end if;
  end;

  /*---------------------------------------------------------------------------
   * Disable() -- PUBLIC
   *-------------------------------------------------------------------------*/
  procedure Disable is
  begin
    g_Enabled := false;
  end;

  /*---------------------------------------------------------------------------
   * Suspend() -- PUBLIC
   *-------------------------------------------------------------------------*/
  procedure Suspend is
  begin
    g_Suspended := true;
  end;

  /*---------------------------------------------------------------------------
   * Resume() -- PUBLIC
   *-------------------------------------------------------------------------*/
  procedure Resume is
  begin
    g_Suspended := false;
  end;

  /*---------------------------------------------------------------------------
   * Shutdown() -- PUBLIC
   *-------------------------------------------------------------------------*/
  procedure Shutdown (
    a_PipeName				varchar2
  ) is
  begin
    Disable();
    dbms_pipe.pack_message(gc_ProtocolVersion);
    dbms_pipe.pack_message(dbms_pipe.unique_session_name);
    dbms_pipe.pack_message('Shutdown');
    if dbms_pipe.send_message(nvl(a_PipeName, g_PipeName), g_TimeOut) != 0 then
      raise_application_error(-20000, 'Unable to send shutdown message!');
    end if;
  end;

  /*---------------------------------------------------------------------------
   * PutLine() -- PUBLIC
   *-------------------------------------------------------------------------*/
  procedure PutLine (
    a_Message				varchar2
  ) is
    c_MessageLength			number := 2000;
    t_NumIters				number(2);
    t_LastMessage			number(1);
  begin
    if g_Enabled and not g_Suspended then
      t_NumIters := nvl(ceil(length(a_Message) / c_MessageLength), 1);
      for i in 1..t_NumIters loop
        t_LastMessage := 0;
        if i = t_NumIters then
          t_LastMessage := 1;
        end if;
        dbms_pipe.pack_message(gc_ProtocolVersion);
        dbms_pipe.pack_message(dbms_pipe.unique_session_name);
        dbms_pipe.pack_message('LogMessage');
        dbms_pipe.pack_message(t_LastMessage);
        dbms_pipe.pack_message(substr(a_Message,
            (i - 1) * c_MessageLength + 1, c_MessageLength));
        if dbms_pipe.send_message(g_PipeName, g_TimeOut) != 0 then
          Disable();
          raise_application_error(-20000, 'Unable to send message!');
        end if;
      end loop;
    end if;
  end;

  /*---------------------------------------------------------------------------
   * PutSingleLine() -- PUBLIC
   *-------------------------------------------------------------------------*/
  procedure PutSingleLine (
    a_Message				varchar2
  ) is
    t_Suspended				boolean;
  begin
    t_Suspended := g_Suspended;
    g_Suspended := false;
    PutLine(a_Message);
    g_Suspended := t_Suspended;
  end;

end pkg_Debug;
/

