<?xml version="1.0" encoding="ISO-8859-1"?>
<!-- Edited by XMLSpy® -->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:template name="PreserveLineBreaks">
    <xsl:param name="text"/>
    <xsl:choose>
      <xsl:when test="contains($text,'&#xA;')">
        <xsl:value-of select="substring-before($text,'&#xA;')" disable-output-escaping="yes"/>
        <br/>
        <xsl:call-template name="PreserveLineBreaks">
          <xsl:with-param name="text">
            <xsl:value-of select="substring-after($text,'&#xA;')" disable-output-escaping="yes"/>
          </xsl:with-param>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$text"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="TEST_REPORT">

    <html>

      <head>

        <style type="text/css">
          BODY
          {
            color:black;
            background-color:white;
            font-family:Consolas;
            font-size:12;
            text-align:center;
          }

          table {
            border-collapse:collapse;
            margin-left:auto;
            margin-right:auto;
          }
          table, th, td {
            border: 1px solid black;
          }

          #header_table {
            border: 1px solid #E3E3E3;
            border-collapse:collapse;
            margin-left:auto;
            margin-right:auto;
          }
          #header_table th, #header_table td {
            border: 1px solid #E3E3E3;
            background-color:#E3E3E3;
          }

          #clean_table {
            border: 1px;
            border-collapse:collapse;
            margin-left:auto;
            margin-right:auto;
          }
          #clean_table th, #clean_table td {
            border: 1px;
          }

          p.footer {
            font-family:Consolas;
            text-align:center;
            font-size: 10px;
          }

          p.t1 {
            font-family:Sans-Serif;
            text-align:center;
            font-size: 20px;
            font-weight:bold;
          }

          p.t11 {
            font-family:Sans-Serif;
            text-align:left;
            font-size: 15px;
            font-weight:bold;
          }

          p.t12 {
            font-family:Sans-Serif;
            text-align:left;
            font-size: 15px;
            font-weight:bold;
          }

          p.t2 {
            font-family:Consolas;
            text-align:center;
            font-size: 12px;
            font-weight:normal;
          }

          p.t3 {
            font-family:Consolas;
            text-align:left;
            font-size: 12px;
            font-weight:normal;
          }

        </style>

      </head>

      <body>

        <h2><p class="t1"><xsl:value-of select="ObjectName"/> Integration Test Report</p></h2>

        <table id="header_table" width="400">
          <col width="150" />
          <col width="250" />
          <tr>
            <th><p class="t3">Component:</p></th>
            <th><p class="t3"><xsl:value-of select="ObjectName"/></p></th>
          </tr>
          <tr>
            <th><p class="t3">Component version:</p></th>
            <th><p class="t3"><xsl:value-of select="TlaVer"/></p></th>
          </tr>
          <tr>
            <th><p class="t3">Date:</p></th>
            <th><p class="t3"><xsl:value-of select="DateTime"/></p></th>
          </tr>
          <tr>
            <th><p class="t3">Author:</p></th>
            <th><p class="t3"><xsl:value-of select="Author"/></p></th>
          </tr>
          <tr>
            <th><p class="t3">SW Branch:</p></th>
            <th><p class="t3"><xsl:value-of select="SwBranch"/></p></th>
          </tr>
          <tr>
            <th><p class="t3">SW SVN revision:</p></th>
            <th><p class="t3"><xsl:value-of select="SvnRev"/></p></th>
          </tr>
          <tr>
            <th><p class="t3">HW version:</p></th>
            <th><p class="t3"><xsl:value-of select="HwVersion"/></p></th>
          </tr>
        </table>
        <br/>
        <br/>

        <table id="clean_table" width="1280">
          <tr>
            <th><p class="t11">TEST SUMMARY</p></th>
          </tr>
        </table>
        <br/>

        <table width="1280">
          <col width="775" />
          <col width="110" />
          <col width="110" />
          <col width="110" />
          <th bgcolor="#D8D8D8"><p class="t2">Test Cases</p></th>
          <th bgcolor="#7BC971"><p class="t2">Tests Passed</p></th>
          <th bgcolor="#ED6161"><p class="t2">Tests Failed</p></th>
          <th bgcolor="grey"><p class="t2">Not Tested</p></th>
            <xsl:for-each select="Collection/Test">
              <tr>
              <th><p class="t3"><xsl:value-of select="TestCase"/></p></th>
              <th><p class="t2"><xsl:value-of select="TestStepsOK"/></p></th>
              <th><p class="t2"><xsl:value-of select="TestStepsNOK"/></p></th>
              <th><p class="t2"><xsl:value-of select="TestStepsNT"/></p></th>
              </tr>
            </xsl:for-each>
          <tr>
            <th bgcolor="#D8D8D8"><p class="t3"><b>TOTAL EXECUTED TESTS: <xsl:value-of select="TotalTestSteps"/></b></p></th>
            <th bgcolor="#D8D8D8"><p class="t2"><b><xsl:value-of select="TotalTestStepsOK"/></b></p></th>
            <th bgcolor="#D8D8D8"><p class="t2"><b><xsl:value-of select="TotalTestStepsNOK"/></b></p></th>
            <th bgcolor="#D8D8D8"><p class="t2"><b><xsl:value-of select="TotalTestStepsNT"/></b></p></th>
          </tr>
        </table>
        <br/>
        <br/>
        <br/>

        <table id="clean_table" width="1280">
          <tr>
            <th><p class="t11">TEST CASES</p></th>
          </tr>
        </table>
        <br/>

        <xsl:for-each select="Collection/Test">
          <table id="clean_table" width="1280">
          <tr>
            <th><p class="t12"><xsl:value-of select="TestCase"/></p></th>
          </tr>
          <tr>
          </tr>
          <tr>
            <th><p class="t3"><xsl:value-of select="TestDescription"/></p></th>
          </tr>
          <tr>
            <th><p class="t3"><xsl:value-of select="TestRequirements"/></p></th>
          </tr>
          </table>

          <table height="30" width="1280">
            <col width="575" />
            <col width="55" />
            <col width="275" />
            <col width="275" />
            <col width="100" />
            <tr bgcolor="#D8D8D8">
              <th><p class="t2">Test Steps</p></th>
              <th><p class="t2">Result</p></th>
			  <th><p class="t2">Actual</p></th>
              <th><p class="t2">Expected</p></th>
              <th><p class="t2">Comments</p></th>
            </tr>
            <xsl:for-each select="TestStep">
              <tr>
                <td>
                  <p class="t3">
                    <xsl:call-template name="PreserveLineBreaks">
                      <xsl:with-param name="text" select='Description'/>
                    </xsl:call-template>
                  </p>
                </td>
                <xsl:choose>
                  <xsl:when test="Result>2">
                    <td bgcolor="grey" align="center"><p class="t2">NT</p></td>
                  </xsl:when>
                  <xsl:when test="Result=2">
                    <td bgcolor="white" align="center"><p class="t2">INFO</p></td>
                  </xsl:when>
                  <xsl:when test="Result=1">
                    <td bgcolor="#7BC971" align="center"><p class="t2">OK</p></td>
                  </xsl:when>
                  <xsl:when test="Result=0">
                    <td bgcolor="#ED6161" align="center"><p class="t2">NOK</p></td>
                  </xsl:when>
                </xsl:choose>
                <td>
                  <p class="t3">
                    <xsl:call-template name="PreserveLineBreaks">
                      <xsl:with-param name="text" select='Actual'/>
                    </xsl:call-template>
                  </p>
                </td>
                <td>
                  <p class="t3">
                    <xsl:call-template name="PreserveLineBreaks">
                      <xsl:with-param name="text" select='Expected'/>
                    </xsl:call-template>
                  </p>
                </td>
                <td>
                  <p class="t3">
                    <xsl:call-template name="PreserveLineBreaks">
                      <xsl:with-param name="text" select='Comment'/>
                    </xsl:call-template>
                  </p>
                </td>
              </tr>
            </xsl:for-each>
          </table>
          <br/>
          <br/>
        </xsl:for-each>
        <br/>

        <p class="footer">Created with Lear LATTE framework</p>

      </body>

    </html>

  </xsl:template>

</xsl:stylesheet>
