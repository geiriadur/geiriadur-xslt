<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:math="http://www.w3.org/2005/xpath-functions/math" exclude-result-prefixes="xs math"
    version="3.0">

    <xsl:template match="/">
        <html>
            <body>
                <!--h2>Word</h2-->
                <table border="1">
                    <!--tr bgcolor="#9acd32">
                        <th>Field</th>
                        <th>Content</th>
                    </tr-->
                    <xsl:for-each select="entry/head">
                        <xsl:for-each select="headword-form">
                            <xsl:if test="string(.) != ''">
                                <tr>
                                    <td>Headword: </td>
                                    <td lang="cy"><xsl:value-of select="."/></td>
                                </tr>
                            </xsl:if>
                        </xsl:for-each>
                        <xsl:for-each select="transcription">
                            <xsl:if test="string(.) != ''">
                                <tr>
                                    <td>IPA: </td>
                                    <td lang="cy-ipa"><xsl:value-of select="."/></td>
                                </tr>
                            </xsl:if>
                        </xsl:for-each>
                        <xsl:for-each select="etymology">
                            <xsl:if test="string(.) != ''">
                                <tr>
                                    <!--td>Etymology: </td-->
                                    <!-- May be one or more of multiple languages /-->
                                    <!--td lang="cel-x-proto"><xsl:value-of select="."/></td-->
                                    <xsl:choose>
                                        <xsl:when test="not(@lang) or @lang=''">
                                            <td>Etymology: </td>
                                            <td><xsl:value-of select="."/></td>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <td>Etymology: </td>
                                            <td lang="{@lang}"><xsl:value-of select="."/></td>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                    <!--td><xsl:value-of select="."/></td-->
                                </tr>
                            </xsl:if>
                        </xsl:for-each>
                        <xsl:for-each select="part-of-speech">
                            <xsl:if test="string(.) != ''">
                                <tr>
                                    <td>Part of Speech: </td>
                                    <td><xsl:value-of select="."/></td>
                                </tr>
                            </xsl:if>
                        </xsl:for-each>
                        <xsl:for-each select="person">
                            <xsl:if test="string(.) != ''">
                                <tr>
                                    <td>Person: </td>
                                    <td><xsl:value-of select="."/></td>
                                </tr>
                            </xsl:if>
                        </xsl:for-each>
                        <xsl:for-each select="gender">
                            <xsl:if test="string(.) != ''">
                                <tr>
                                    <td>Gender: </td>
                                    <td><xsl:value-of select="."/></td>
                                </tr>
                            </xsl:if>
                        </xsl:for-each>
                        <xsl:for-each select="number">
                            <xsl:if test="string(.) != ''">
                                <tr>
                                    <td>Number: </td>
                                    <td><xsl:value-of select="."/></td>
                                </tr>
                            </xsl:if>
                        </xsl:for-each>
                        <xsl:for-each select="plural">
                            <xsl:for-each select="plural-form">
                                <tr><td></td><td></td></tr>
                                <xsl:if test="string(.) != ''">
                                    <tr>
                                        <td>Plural: </td>
                                        <td lang="cy"><xsl:value-of select="."/>
                                            <!-- Add (note) only if @note exists and is not empty -->
                                            <xsl:if test="@note">
                                                <xsl:text> (</xsl:text>
                                                <xsl:value-of select="@note"/>
                                                    <xsl:text>)</xsl:text>
                                            </xsl:if>
                                        </td>
                                    </tr>
                                </xsl:if>
                            </xsl:for-each>
                            <xsl:for-each select="transcription">
                                <xsl:if test="string(.) != ''">
                                    <tr>
                                        <td>IPA: </td>
                                        <td lang="cy-ipa"><xsl:value-of select="."/>
                                            <!-- Add (note) only if @note exists and is not empty -->
                                            <xsl:if test="@note">
                                                <xsl:text> (</xsl:text>
                                                <xsl:value-of select="@note"/>
                                                <xsl:text>)</xsl:text>
                                            </xsl:if>
                                        </td>
                                    </tr>
                                </xsl:if>
                            </xsl:for-each>
                            <xsl:for-each select="etymology">
                                <xsl:if test="string(.) != ''">
                                    <tr>
                                        <td>Etymology: </td>
                                        <!-- May be one or more of multiple languages /-->
                                        <!--td lang="cel-x-proto"><xsl:value-of select="."/></td-->
                                        <td><xsl:value-of select="."/>
                                            <!-- Add (note) only if @note exists and is not empty -->
                                            <xsl:if test="@note">
                                                <xsl:text> (</xsl:text>
                                                <xsl:value-of select="@note"/>
                                                <xsl:text>)</xsl:text>
                                            </xsl:if>
                                        </td>
                                    </tr>
                                </xsl:if>
                            </xsl:for-each>
                        </xsl:for-each>
                    </xsl:for-each>
                    <xsl:for-each select="entry/body/sense">
                        <tr><td></td><td></td></tr>
                        <xsl:for-each select="translation">
                            <xsl:if test="string(.) != ''">
                                <tr>
                                    <xsl:choose>
                                        <xsl:when test="not(@lang) or @lang=''">
                                            <td>Sense: </td>
                                            <td><xsl:value-of select="."/></td>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <td>Sense: </td>
                                            <td lang="{@lang}"><xsl:value-of select="."/></td>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </tr>
                            </xsl:if>
                        </xsl:for-each>
                    </xsl:for-each>
                    <xsl:for-each select="entry/body/sense">
                        <tr><td></td><td></td></tr>
                        <xsl:for-each select="notes">
                            <xsl:if test="string(.) != ''">
                                <tr>
                                    <xsl:choose>
                                        <xsl:when test="not(@lang) or @lang=''">
                                            <td>Notes: </td>
                                            <td><xsl:value-of select="."/></td>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <td>Notes: </td>
                                            <td lang="{@lang}"><xsl:value-of select="."/></td>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </tr>
                            </xsl:if>
                        </xsl:for-each>
                    </xsl:for-each>
                </table>
            </body>
        </html>
    </xsl:template>

</xsl:stylesheet>
